# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

from django.test import SimpleTestCase

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKER_ENTRYPOINT = REPO_ROOT / "docker" / "entrypoints" / "celery_chatbot.sh"
# A cold django.setup() imports every plugin module, so this is generous on purpose: it is a guard
# against a hung interpreter, not a latency assertion, and a slow CI box must not flake on it.
PROBE_TIMEOUT_SECONDS = 300

# Settings are read at import time, so the effect of an environment variable can only be observed
# in a freshly booted interpreter: override_settings would assign the value we are trying to prove
# is computed, and reloading the settings package in-process corrupts it for every other test.
# This probe reports what a real deployment would end up with, from the setting down to the queue
# the chat task is actually routed to. The task name is read from the task itself so a drift
# between the route key and the real name surfaces here too.
SETTINGS_PROBE = """
import json

import django

django.setup()

from api_app.chatbot_manager.tasks import process_chat_message
from django.conf import settings
from intel_owl.celery import app, get_queue_name

print(
    json.dumps(
        {
            "chatbot_queue": settings.CHATBOT_QUEUE,
            "celery_queues": settings.CELERY_QUEUES,
            "routed_queue": app.conf.task_routes[process_chat_message.name]["queue"],
            "declared_queues": [queue.name for queue in app.conf.task_queues],
            "expected_queue_name": get_queue_name(settings.CHATBOT_QUEUE),
        }
    )
)
"""


class ChatbotQueueSettingTestCase(SimpleTestCase):
    """The chatbot queue name must be configurable end to end: whatever the environment says has
    to reach ``settings.CHATBOT_QUEUE`` *and* the Celery route of the chat task, otherwise turns
    are published to a queue no worker drains."""

    def _boot_settings(self, chatbot_queue: Optional[str] = None) -> Dict:
        """Boot Django in a subprocess with CHATBOT_QUEUE set to *chatbot_queue* (unset when None)
        and return the probe's report. Fails the test if the interpreter does not exit cleanly."""
        env = os.environ.copy()
        env["DJANGO_SETTINGS_MODULE"] = "intel_owl.settings"
        if chatbot_queue is None:
            env.pop("CHATBOT_QUEUE", None)
        else:
            env["CHATBOT_QUEUE"] = chatbot_queue
        result = subprocess.run(
            [sys.executable, "-c", SETTINGS_PROBE],
            capture_output=True,
            cwd=REPO_ROOT,
            env=env,
            text=True,
            timeout=PROBE_TIMEOUT_SECONDS,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"settings probe crashed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        # django.setup() is free to log on the way up, so only the last line is the payload
        return json.loads(result.stdout.strip().splitlines()[-1])

    def test_custom_chatbot_queue_reaches_settings_and_task_routing(self):
        booted = self._boot_settings(chatbot_queue="my_custom_queue")

        self.assertEqual(booted["chatbot_queue"], "my_custom_queue")
        self.assertIn("my_custom_queue", booted["celery_queues"])
        # get_queue_name appends .fifo under SQS, so compare against what the deployment derives
        self.assertEqual(booted["routed_queue"], booted["expected_queue_name"])
        self.assertIn(
            booted["expected_queue_name"],
            booted["declared_queues"],
            msg="the chat task is routed to a queue that is never declared",
        )

    def test_chatbot_queue_falls_back_to_the_default_when_unset_or_blank(self):
        for chatbot_queue in (None, ""):
            with self.subTest(chatbot_queue=chatbot_queue):
                booted = self._boot_settings(chatbot_queue=chatbot_queue)

                self.assertEqual(booted["chatbot_queue"], "chatbot")
                self.assertIn("chatbot", booted["celery_queues"])

    def test_worker_entrypoint_derives_its_queue_from_the_setting(self):
        """Django publishes the chat task and the dedicated worker consumes it, each reading
        CHATBOT_QUEUE on its own side. Re-hardcoding either one, or letting the two defaults drift,
        silently sends turns to a queue nobody drains -- the same failure this setting already had,
        one layer down. Only the shell can be checked statically, so it is checked here."""
        script = WORKER_ENTRYPOINT.read_text()

        shell_default = re.search(r"\$\{CHATBOT_QUEUE:-([^}]+)\}", script)
        self.assertIsNotNone(
            shell_default,
            msg="the worker entrypoint no longer derives its queue from CHATBOT_QUEUE",
        )
        self.assertEqual(
            shell_default.group(1),
            self._boot_settings()["chatbot_queue"],
            msg="the entrypoint's default queue differs from the one the settings fall back to",
        )
        for hardcoded in ('queues="chatbot', "chatbot.fifo"):
            self.assertNotIn(
                hardcoded,
                script,
                msg=f"{hardcoded!r} is hardcoded again in the worker entrypoint",
            )

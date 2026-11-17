# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

# this module must run before the others

from ._util import get_secret
from .aws import AWS_SQS

RESULT_BACKEND = "django-db"
BROKER_URL = get_secret("BROKER_URL", None)
if not BROKER_URL:
    if AWS_SQS:
        BROKER_URL = "sqs://"
    else:
        BROKER_URL = "redis://redis:6379/1"  # 0 is used by channels

DEFAULT_QUEUE = "default"
BROADCAST_QUEUE = "broadcast"
CONFIG_QUEUE = "config"

# The dedicated chatbot worker consumes this same variable (docker/entrypoints/celery_chatbot.sh),
# so the queue the chat task is published to and the queue that worker drains cannot drift apart.
# `or` instead of a default argument: an empty value falls back like the shell's
# ${CHATBOT_QUEUE:-chatbot}, so both ends agree on unset *and* blank. Read from the environment
# only (not intel_owl.secrets, which would also consult AWS Secrets Manager) precisely because the
# worker entrypoint is a shell script: a value only Django could resolve would re-create the drift.
CHATBOT_QUEUE = get_secret("CHATBOT_QUEUE") or "chatbot"

CELERY_QUEUES = get_secret("CELERY_QUEUES", DEFAULT_QUEUE).split(",")
for queue in [DEFAULT_QUEUE, CONFIG_QUEUE, CHATBOT_QUEUE]:
    if queue not in CELERY_QUEUES:
        CELERY_QUEUES.append(queue)

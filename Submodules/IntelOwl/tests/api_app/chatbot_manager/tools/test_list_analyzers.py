# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

import json

from django.test import TestCase

from api_app.analyzers_manager.constants import TypeChoices
from api_app.analyzers_manager.models import AnalyzerConfig
from api_app.chatbot_manager.agent.tools import build_tools
from api_app.chatbot_manager.agent.tools._common import MAX_RESULTS
from api_app.models import OrganizationPluginConfiguration
from certego_saas.apps.organization.membership import Membership
from certego_saas.apps.organization.organization import Organization
from certego_saas.apps.user.models import User


class ListAnalyzersToolTestCase(TestCase):
    def setUp(self):
        self.org_user, _ = User.objects.get_or_create(username="list_analyzers_org_user")
        self.outsider, _ = User.objects.get_or_create(username="list_analyzers_outsider")
        self.org, _ = Organization.objects.get_or_create(name="list analyzers organization")
        Membership.objects.get_or_create(user=self.org_user, organization=self.org, is_owner=True)

        # A real seeded observable analyzer (constructing one would need a PythonModule FK).
        self.analyzer = (
            AnalyzerConfig.objects.filter(
                type=TypeChoices.OBSERVABLE,
                observable_supported__contains=["domain"],
                disabled=False,
            )
            .order_by("name")
            .first()
        )
        self.assertIsNotNone(self.analyzer, "expected a seeded observable analyzer supporting 'domain'")

        # Disable it for self.org: the per-user `runnable` flag must flip to False, but the
        # analyzer must still be listed (analyzer configs are global, non-sensitive).
        self.org_disable = OrganizationPluginConfiguration.objects.create(
            config=self.analyzer, organization=self.org, disabled=True
        )

        self.list_analyzers = {t.name: t for t in build_tools(user=self.org_user)}["list_analyzers"]

    def tearDown(self):
        self.org_disable.delete()
        Membership.objects.filter(organization=self.org).delete()
        self.org.delete()

    def test_list_analyzers_filters_by_observable_type(self):
        data = json.loads(self.list_analyzers.invoke({"observable_type": "domain"}))
        self.assertEqual(data["errors"], [])
        self.assertTrue(data["analyzers"])
        # every returned analyzer supports the requested observable type
        for analyzer in data["analyzers"]:
            self.assertIn("domain", analyzer["observable_supported"])
        names = [a["name"] for a in data["analyzers"]]
        self.assertIn(self.analyzer.name, names)

    def test_list_analyzers_unknown_observable_type(self):
        data = json.loads(self.list_analyzers.invoke({"observable_type": "bogus"}))
        # invalid type is reported and the filter is ignored (results still returned)
        self.assertTrue(data["errors"])
        self.assertIn("Unknown observable_type", data["errors"][0])
        self.assertTrue(data["analyzers"])

    def test_list_analyzers_limit(self):
        data = json.loads(self.list_analyzers.invoke({"limit": 1}))
        self.assertEqual(len(data["analyzers"]), 1)

    def test_list_analyzers_limit_clamps_to_max(self):
        # An over-cap limit from the LLM is clamped to MAX_RESULTS (untrusted arg): the seeded
        # observable analyzers exceed the cap, so the result is capped, never the requested 999.
        # The clamp is surfaced in `errors` so a truncated list isn't silent.
        data = json.loads(self.list_analyzers.invoke({"limit": 999}))
        self.assertLessEqual(len(data["analyzers"]), MAX_RESULTS)
        self.assertTrue(any("exceeds the maximum" in e for e in data["errors"]))

    def test_list_analyzers_org_disabled_runnable_flag(self):
        # Deterministic, one-directional isolation check: an analyzer disabled for the user's
        # organization comes back with runnable=False AND is still present in the list (it is
        # not hidden -- list_analyzers lists, it does not filter on runnable). We do NOT assert
        # the contrasting runnable=True for an outsider, because `runnable` also folds in
        # configured+healthy, which a key-based analyzer lacks on a test deploy without keys.
        rows = {
            a["name"]: a
            for a in json.loads(self.list_analyzers.invoke({"observable_type": "domain"}))["analyzers"]
        }
        self.assertIn(self.analyzer.name, rows)
        self.assertFalse(rows[self.analyzer.name]["runnable"])

        # The same analyzer is still listed for an unaffiliated user (global, non-sensitive).
        outsider_tool = {t.name: t for t in build_tools(user=self.outsider)}["list_analyzers"]
        outsider_names = [
            a["name"] for a in json.loads(outsider_tool.invoke({"observable_type": "domain"}))["analyzers"]
        ]
        self.assertIn(self.analyzer.name, outsider_names)

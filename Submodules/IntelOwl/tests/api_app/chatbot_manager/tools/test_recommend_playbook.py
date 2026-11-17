# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

import json

from django.test import TestCase

from api_app.chatbot_manager.agent.tools import build_tools
from api_app.choices import ScanMode
from api_app.playbooks_manager.models import PlaybookConfig
from certego_saas.apps.organization.membership import Membership
from certego_saas.apps.organization.organization import Organization
from certego_saas.apps.user.models import User


class RecommendPlaybookToolTestCase(TestCase):
    def setUp(self):
        self.user, _ = User.objects.get_or_create(username="recommend_pb_user")
        # Another member of the same org: used to test org-shared vs private visibility.
        self.org_member, _ = User.objects.get_or_create(username="recommend_pb_org_member")
        self.org, _ = Organization.objects.get_or_create(name="recommend pb organization")
        Membership.objects.get_or_create(user=self.user, organization=self.org, is_owner=True)
        Membership.objects.get_or_create(user=self.org_member, organization=self.org, is_owner=False)

        self.pb_owned = PlaybookConfig.objects.create(
            name="recommend_pb_owned", description="t", type=["ip"], owner=self.user, starting=True
        )
        # Owned by another member of the same org and shared at org level -> visible.
        self.pb_org_shared = PlaybookConfig.objects.create(
            name="recommend_pb_org_shared",
            description="t",
            type=["ip"],
            owner=self.org_member,
            for_organization=True,
            starting=True,
        )
        # Owned by another member but NOT shared -> must stay invisible to self.user.
        self.pb_private_other = PlaybookConfig.objects.create(
            name="recommend_pb_private_other",
            description="t",
            type=["ip"],
            owner=self.org_member,
            for_organization=False,
            starting=True,
        )
        # Not directly launchable -> must not be recommended. A non-starting playbook must force
        # new analysis with no check time (model clean()), which create() enforces.
        self.pb_not_starting = PlaybookConfig.objects.create(
            name="recommend_pb_not_starting",
            description="t",
            type=["ip"],
            owner=self.user,
            starting=False,
            scan_mode=ScanMode.FORCE_NEW_ANALYSIS.value,
            scan_check_time=None,
        )
        # Disabled -> must not be recommended.
        self.pb_disabled = PlaybookConfig.objects.create(
            name="recommend_pb_disabled",
            description="t",
            type=["ip"],
            owner=self.user,
            starting=True,
            disabled=True,
        )
        # Different classification -> must not match an ip observable.
        self.pb_domain = PlaybookConfig.objects.create(
            name="recommend_pb_domain", description="t", type=["domain"], owner=self.user, starting=True
        )

        self.recommend_playbook = {t.name: t for t in build_tools(user=self.user)}["recommend_playbook"]

    def tearDown(self):
        PlaybookConfig.objects.filter(owner__in=[self.user, self.org_member]).delete()
        Membership.objects.filter(organization=self.org).delete()
        self.org.delete()

    def test_recommend_playbook_derives_classification_from_observable(self):
        data = json.loads(self.recommend_playbook.invoke({"observable_name": "8.8.8.8"}))
        self.assertEqual(data["errors"], [])
        names = [p["name"] for p in data["playbooks"]]
        # 8.8.8.8 is classified as ip -> the ip playbook matches, the domain one does not
        self.assertIn(self.pb_owned.name, names)
        self.assertNotIn(self.pb_domain.name, names)

    def test_recommend_playbook_explicit_classification(self):
        data = json.loads(self.recommend_playbook.invoke({"classification": "ip"}))
        self.assertEqual(data["errors"], [])
        names = [p["name"] for p in data["playbooks"]]
        self.assertIn(self.pb_owned.name, names)

    def test_recommend_playbook_invalid_classification(self):
        data = json.loads(self.recommend_playbook.invoke({"classification": "bogus"}))
        self.assertTrue(data["errors"])
        self.assertIn("Unknown classification", data["errors"][0])
        self.assertEqual(data["playbooks"], [])

    def test_recommend_playbook_requires_input(self):
        data = json.loads(self.recommend_playbook.invoke({}))
        self.assertTrue(data["errors"])
        self.assertEqual(data["playbooks"], [])

    def test_recommend_playbook_only_starting_and_enabled(self):
        names = [
            p["name"]
            for p in json.loads(self.recommend_playbook.invoke({"classification": "ip"}))["playbooks"]
        ]
        self.assertIn(self.pb_owned.name, names)
        self.assertNotIn(self.pb_not_starting.name, names)
        self.assertNotIn(self.pb_disabled.name, names)

    def test_recommend_playbook_visibility_isolation(self):
        names = [
            p["name"]
            for p in json.loads(self.recommend_playbook.invoke({"classification": "ip"}))["playbooks"]
        ]
        # owned + org-shared are visible
        self.assertIn(self.pb_owned.name, names)
        self.assertIn(self.pb_org_shared.name, names)
        # another member's private playbook is NOT visible
        self.assertNotIn(self.pb_private_other.name, names)

    def test_recommend_playbook_limit(self):
        # Two visible, starting, enabled ip playbooks match (owned + org-shared); the cap must
        # trim the result to the requested size.
        all_matches = json.loads(self.recommend_playbook.invoke({"classification": "ip"}))["playbooks"]
        self.assertGreaterEqual(len(all_matches), 2)
        capped = json.loads(self.recommend_playbook.invoke({"classification": "ip", "limit": 1}))
        self.assertEqual(len(capped["playbooks"]), 1)

    def test_recommend_playbook_limit_clamp_warns(self):
        # An over-cap limit is clamped to MAX_RESULTS and the clamp is surfaced in `errors`,
        # regardless of how many playbooks actually match (999 > 50 always warns).
        data = json.loads(self.recommend_playbook.invoke({"classification": "ip", "limit": 999}))
        self.assertTrue(any("exceeds the maximum" in e for e in data["errors"]))

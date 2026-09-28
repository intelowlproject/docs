# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

from unittest.mock import MagicMock, patch

from django.test import override_settings

from api_app.connectors_manager.connectors.slack import Slack
from tests.api_app.connectors_manager.unit_tests.base_test_class import BaseConnectorTest


class SlackTestCase(BaseConnectorTest):
    connector_class = Slack

    @classmethod
    def get_extra_config(cls) -> dict:
        return {
            "_channel": "ABCD",
            "slack_username": "intelowl_bot",
            "_token": "mock-token-123",
        }

    def _setup_connector(self):
        connector = super()._setup_connector()
        connector._job.url = "https://intelowl.example.com/jobs/51"
        mock_client = MagicMock()
        mock_client.chat_postMessage.return_value = {"ok": True}
        connector.client = mock_client
        return connector

    @staticmethod
    def get_mocked_response():
        return [patch("api_app.connectors_manager.connectors.slack.slack_sdk.WebClient")]

    def test_slack_message_content(self):
        connector = self._setup_connector()

        self.assertEqual(connector.title, "*IntelOwl analysis*")
        self.assertIn("intelowl_bot", connector.body)
        self.assertIn("1.1.1.1", connector.body)
        self.assertIn("https://intelowl.example.com/jobs/51", connector.body)

    @override_settings(STAGE_CI=False, MOCK_CONNECTIONS=False)
    def test_slack_health_check_success(self):
        connector = self._setup_connector()

        mock_token_param = MagicMock()
        mock_token_param.name = "token"
        mock_token_param.value = "mock-token-123"

        connector._config = MagicMock()
        connector._config.parameters.annotate_configured.return_value.annotate_value_for_user.return_value = [
            mock_token_param
        ]

        with patch("api_app.connectors_manager.connectors.slack.slack_sdk.WebClient") as mock_webclient_cls:
            mock_instance = mock_webclient_cls.return_value
            mock_instance.auth_test.return_value = {"ok": True}

            self.assertTrue(connector.health_check()[0])

    @override_settings(STAGE_CI=False, MOCK_CONNECTIONS=False)
    def test_slack_health_check_failures(self):
        connector = self._setup_connector()

        mock_token_param = MagicMock()
        mock_token_param.name = "token"
        mock_token_param.value = "mock-token-123"

        connector._config = MagicMock()
        connector._config.parameters.annotate_configured.return_value.annotate_value_for_user.return_value = [
            mock_token_param
        ]

        with (
            self.subTest("Slack Connection/Token Exception"),
            patch("api_app.connectors_manager.connectors.slack.slack_sdk.WebClient") as mock_webclient_cls,
        ):
            mock_instance = mock_webclient_cls.return_value
            mock_instance.auth_test.side_effect = Exception("invalid_auth")
            self.assertFalse(connector.health_check()[0])

        with self.subTest("Missing Token Configuration"):
            connector._config.parameters.annotate_configured.return_value.annotate_value_for_user.return_value = []
            self.assertFalse(connector.health_check()[0])

from api_app.analyzers_manager.exceptions import AnalyzerConfigurationException
from api_app.analyzers_manager.observable_analyzers.hudsonrock import HudsonRock
from tests.api_app.analyzers_manager.unit_tests.observable_analyzers.base_test_class import (
    BaseAnalyzerTest,
)
from tests.mock_utils import MockUpResponse, patch


class HudsonRockTestCase(BaseAnalyzerTest):
    analyzer_class = HudsonRock

    @classmethod
    def get_extra_config(cls):
        return {
            "_api_key_name": "dummy-api-key",
            "observable_classification": "generic",  # to test login path
            "observable_name": "test@example.com",
            "page": 1,
            "sort_by": "asc",
            "installed_software": False,
        }

    @staticmethod
    def get_mocked_response():
        return patch(
            "requests.post",
            return_value=MockUpResponse(
                {
                    "credentials": [
                        {
                            "type": "client",
                            "domain": "disney.com",
                            "username": "••••",
                            "password": "••••",
                        }
                    ]
                },
                200,
            ),
        )

    def test_generic_non_email_raises_exception(self):
        """Test that non-email GENERIC observable raises AnalyzerConfigurationException."""
        analyzer = HudsonRock.__new__(HudsonRock)
        analyzer._api_key_name = "dummy-api-key"
        analyzer.observable_classification = "generic"
        analyzer.observable_name = "johndoe123"
        analyzer.url = "https://cavalier.hudsonrock.com/api/json/v2"
        analyzer.compromised_since = None
        analyzer.compromised_until = None
        analyzer.page = None
        analyzer.added_since = None
        analyzer.added_until = None
        analyzer.installed_software = None
        analyzer.sort_by = None
        analyzer.domain_cred_type = None
        analyzer.domain_filtered = None
        analyzer.third_party_domains = None

        with self.assertRaises(AnalyzerConfigurationException) as context:
            analyzer.run()
        self.assertIn("not a valid email", str(context.exception))

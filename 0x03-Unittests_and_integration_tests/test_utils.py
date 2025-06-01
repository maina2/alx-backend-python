#!/usr/bin/env python3
"""Unit tests for client module."""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, Mock, PropertyMock
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD
from typing import Dict, List


class TestGithubOrgClient(unittest.TestCase):
    """Test GithubOrgClient class."""
    @parameterized.expand([
        ("google", {
            "login": "google",
            "id": 1342004,
            "repos_url": "https://api.github.com/orgs/google/repos"
        }),
        ("abc", {
            "login": "abc",
            "id": 1234567,
            "repos_url": "https://api.github.com/orgs/abc/repos"
        }),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, expected_payload: Dict,
                 mock_get_json: Mock) -> None:
        """Test GithubOrgClient.org returns correct payload."""
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        result = client.org
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self) -> None:
        """Test _public_repos_url returns correct URL."""
        test_payload = {
            "login": "test_org",
            "id": 9999999,
            "repos_url": "https://api.github.com/orgs/test_org/repos",
            "type": "Organization"
        }
        with patch.object(GithubOrgClient, 'org',
                          new_callable=PropertyMock) as mock_org:
            mock_org.return_value = test_payload
            client = GithubOrgClient("test_org")
            result = client._public_repos_url
            self.assertEqual(result, test_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """Test public_repos returns correct repo names."""
        test_payload = [
            {"name": "repo1"},
            {"name": "repo2"}
        ]
        mock_get_json.return_value = test_payload
        test_url = "https://api.github.com/orgs/test_org/repos"

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_url:
            mock_public_url.return_value = test_url
            client = GithubOrgClient("test_org")
            result = client.public_repos(license=None)

            self.assertEqual(result, ["repo1", "repo2"])
            mock_get_json.assert_called_once_with(test_url)
            mock_public_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo: Dict, key: str,
                         expectation: bool) -> None:
        """Test has_license checks license key."""
        result = GithubOrgClient.has_license(repo, key)
        self.assertEqual(result, expectation)


@parameterized_class(
    ['org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'],
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient."""
    @classmethod
    def setUpClass(cls):
        """Set up patch for requests."""
        cls.get_patcher = patch(
            'requests.get',
            side_effect=[cls.org_payload, cls.repos_payload]
        )
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down patch."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos integration."""
        pass

    def test_public_repos_with_license(self):
        """Test public_repos with license."""
        pass


if __name__ == "__main__":
    unittest.main()
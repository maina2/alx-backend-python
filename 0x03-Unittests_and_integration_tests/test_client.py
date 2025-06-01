#!/usr/bin/env python3
"""Unit tests for client module.
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient
from typing import Dict


class TestGithubOrgClient(unittest.TestCase):
    """Test case for GithubOrgClient class.
    """
    @parameterized.expand([
        (
            "google",
            {
                "login": "google",
                "id": 1342004,
                "repos_url": "https://api.github.com/orgs/google/repos",
                "type": "Organization"
            }
        ),
        (
            "abc",
            {
                "login": "abc",
                "id": 1234567,
                "repos_url": "https://api.github.com/orgs/abc/repos",
                "type": "Organization"
            }
        ),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, expected_payload: Dict, mock_get_json: Mock) -> None:
        """Test GithubOrgClient.org returns expected payload and calls get_json once."""
        print(f"Testing org_name: {org_name}")
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        result = client.org
        print(f"Mock called: {mock_get_json.called}, Call args: {mock_get_json.call_args}")
        print(f"Result: {result}, Expected: {expected_payload}")
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self) -> None:
        """Test GithubOrgClient._public_repos_url returns expected URL from mocked org payload."""
        test_payload = {
            "login": "test_org",
            "id": 9999999,
            "repos_url": "https://api.github.com/orgs/test_org/repos",
            "type": "Organization"
        }
        with patch('client.GithubOrgClient.org', new_callable=PropertyMock) as mock_org:
            print(f"Mock org setup: {mock_org.return_value}")
            mock_org.return_value = test_payload
            client = GithubOrgClient("test_org")
            result = client._public_repos_url
            print(f"Result: {result}, Expected: {test_payload['repos_url']}")
            self.assertEqual(result, test_payload["repos_url"])


if __name__ == "__main__":
    unittest.main()
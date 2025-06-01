#!/usr/bin/env python3
"""Unit tests for client module.
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from client import GithubOrgClient
from typing import Dict


class TestGithubOrgClient(unittest.TestCase):
    """Test case for GithubOrgClient class.
    """
    @parameterized.expand([
        ("google", {"login": "google", "repos_url": "https://api.github.com/orgs/google/repos"}),
        ("abc", {"login": "abc", "repos_url": "https://api.github.com/orgs/abc/repos"}),
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


if __name__ == "__main__":
    unittest.main()
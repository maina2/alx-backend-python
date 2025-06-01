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
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('client.get_json')
    def test_org_client(self, org_name: str, expected_payload: Dict, mock_get_json: Mock) -> None:
        """Test GithubOrgClient.org with client.get_json mock."""
        print(f"Testing org_name: {org_name} with client.get_json mock")
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        result = client.org
        print(f"Mock called: {mock_get_json.called}, Call args: {mock_get_json.call_args}")
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, expected_payload)

    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('utils.get_json')
    def test_org_utils(self, org_name: str, expected_payload: Dict, mock_get_json: Mock) -> None:
        """Test GithubOrgClient.org with utils.get_json mock."""
        print(f"Testing org_name: {org_name} with utils.get_json mock")
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        result = client.org
        print(f"Mock called: {mock_get_json.called}, Call args: {mock_get_json.call_args}")
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, expected_payload)


if __name__ == "__main__":
    unittest.main()
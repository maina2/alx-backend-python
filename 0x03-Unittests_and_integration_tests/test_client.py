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
    def test_org(self, org_name: str, expected_payload: Dict, mock_get_json: Mock) -> None:
        """Test GithubOrgClient.org returns expected payload and calls get_json once."""
        # Set up mock to return expected_payload when called
        mock_get_json.return_value = expected_payload
        # Create GithubOrgClient instance
        client = GithubOrgClient(org_name)
        # Call org property
        result = client.org
        # Verify get_json was called once with correct URL
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        # Verify result matches expected payload
        self.assertEqual(result, expected_payload)


if __name__ == "__main__":
    unittest.main()
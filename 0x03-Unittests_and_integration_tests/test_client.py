#!/usr/bin/env python3
"""Unit tests for client module.
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from client import GithubOrgClient
from utils import get_json
from typing import Dict


class TestGithubOrgClient(unittest.TestCase):
    """Test case for GithubOrgClient class.
    """
    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('utils.get_json')
    def test_org(self, org_name: str, expected_payload: Dict, mock_get_json: Mock) -> None:
        """Test GithubOrgClient.org returns expected payload and calls get_json once."""
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        result = client.org
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, expected_payload)


if __name__ == "__main__":
    unittest.main()
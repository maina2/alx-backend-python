#!/usr/bin/env python3
"""Unit tests for utils module.
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from typing import Mapping, Sequence, Any, Dict


class TestAccessNestedMap(unittest.TestCase):
    """Test case for access_nested_map function.
    """
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map: Mapping, path: Sequence, expected: Any) -> None:
        """Test access_nested_map returns expected value for given nested map and path."""
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map: Mapping, path: Sequence, expected_key: str) -> None:
        """Test access_nested_map raises KeyError with expected key for invalid paths."""
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """Test case for get_json function.
    """
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('requests.get')
    def test_get_json(self, test_url: str, test_payload: Dict, mock_get: Mock) -> None:
        """Test get_json returns expected payload and calls requests.get once with test_url."""
        mock_get.return_value = Mock(json=lambda: test_payload)
        result = get_json(test_url)
        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test case for memoize decorator.
    """
    @patch.object('utils.TestClass.a_method', return_value=42)
    def test_memoize(self, mock_a_method: Mock) -> None:
        """Test memoize decorator caches a_method result and calls it only once."""
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        test_obj = TestClass()
        result1 = test_obj.a_property
        result2 = test_obj.a_property
        self.assertEqual(result1, 42)
        self.assertEqual(result2, 42)
        mock_a_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
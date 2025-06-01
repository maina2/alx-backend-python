GitHub Organization Client
Overview
This project implements a GitHub organization client in Python 3.7, designed to interact with the GitHub API to retrieve organization details and public repository information. It includes utility functions for accessing nested dictionaries, fetching JSON data, and memoizing method results, along with a client class to query GitHub organization data.
Requirements

Environment: Python 3.7 on Ubuntu 18.04 LTS
Code Style: Pycodestyle 2.5
Dependencies: requests, parameterized (for testing)
Files:
utils.py: Utility functions for accessing nested maps, fetching JSON, and memoization.
client.py: GithubOrgClient class for interacting with the GitHub API.
fixtures.py: Test fixtures for mocking GitHub API responses.
test_utils.py: Unit tests for the utils module.
README.md: This file.



Setup

Clone the repository or ensure all project files are in the same directory.
Install dependencies:pip install requests parameterized


Make files executable:chmod +x *.py


Verify Python version:python3 --version

Ensure it outputs Python 3.7.x.

Running Tests
To run the unit tests for the utils module:
python3 -m unittest test_utils.py

This executes the test cases in test_utils.py, which verify the functionality of access_nested_map and other utility functions.
Project Structure

utils.py: Contains access_nested_map, get_json, and memoize functions with type annotations and documentation.
client.py: Implements GithubOrgClient to fetch organization and repository data, using memoization for efficiency.
fixtures.py: Provides test data for mocking GitHub API responses.
test_utils.py: Includes unit tests for utils.py, using unittest and parameterized for parameterized testing.

Testing Details
The test_utils.py file currently tests the access_nested_map function with the following cases:

{"a": 1}, ("a",) → Returns 1
{"a": {"b": 2}}, ("a",) → Returns {"b": 2}
{"a": {"b": 2}}, ("a", "b") → Returns 2

Additional tests for exception handling (e.g., KeyError) and other functions may be added as per assignment requirements.
Notes

All Python files start with #!/usr/bin/env python3 and end with a newline.
Code adheres to pycodestyle 2.5 standards.
All modules, classes, and functions include proper documentation and type annotations, verifiable via:python3 -c 'print(__import__("utils").__doc__)'
python3 -c 'print(__import__("utils").access_nested_map.__doc__)'



For further information or to contribute, please review the code and submit pull requests via GitHub.

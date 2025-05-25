# """Tests for PyWebGuard command-line interface."""

# import pytest
# import os
# import json
# import tempfile
# from typing import Dict, Any, cast
# from unittest.mock import patch, MagicMock

# from pywebguard.cli import main


# class TestCLI:
#     """Tests for PyWebGuard CLI."""

#     def test_version(self):
#         """Test the --version flag."""
#         with patch("sys.argv", ["pywebguard", "--version"]):
#             with patch("builtins.print") as mock_print:
#                 assert main() == 0
#                 mock_print.assert_called_once()
#                 assert "PyWebGuard v" in mock_print.call_args[0][0]

#     def test_init_command(self):
#         """Test the init command."""
#         with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
#             try:
#                 # Run the init command
#                 with patch(
#                     "sys.argv", ["pywebguard", "init", "--output", temp_file.name]
#                 ):
#                     assert main() == 0

#                 # Check that the file was created
#                 assert os.path.exists(temp_file.name)

#                 # Check that the file contains valid JSON
#                 with open(temp_file.name, "r") as f:
#                     config = json.load(f)

#                 # Check that the config has the expected sections
#                 assert "ip_filter" in config
#                 assert "rate_limit" in config
#                 assert "user_agent" in config
#                 assert "penetration" in config
#                 assert "cors" in config
#                 assert "logging" in config
#                 assert "storage" in config
#             finally:
#                 # Clean up
#                 os.unlink(temp_file.name)

#     def test_init_command_with_framework(self):
#         """Test the init command with a framework."""
#         with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
#             try:
#                 # Run the init command with a framework
#                 with patch(
#                     "sys.argv",
#                     [
#                         "pywebguard",
#                         "init",
#                         "--output",
#                         temp_file.name,
#                         "--framework",
#                         "fastapi",
#                     ],
#                 ):
#                     assert main() == 0

#                 # Check that the file was created
#                 assert os.path.exists(temp_file.name)

#                 # Check that the file contains valid JSON
#                 with open(temp_file.name, "r") as f:
#                     config = json.load(f)

#                 # Check that the config has the framework section
#                 assert "framework" in config
#                 assert config["framework"]["type"] == "fastapi"
#                 assert "route_rate_limits" in config["framework"]
#             finally:
#                 # Clean up
#                 os.unlink(temp_file.name)

#     def test_validate_command(self):
#         """Test the validate command."""
#         with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
#             try:
#                 # Create a valid config file
#                 config = {
#                     "ip_filter": {
#                         "enabled": True,
#                         "whitelist": [],
#                         "blacklist": [],
#                         "block_cloud_providers": False,
#                         "geo_restrictions": {},
#                     },
#                     "rate_limit": {
#                         "enabled": True,
#                         "requests_per_minute": 60,
#                         "burst_size": 10,
#                         "auto_ban_threshold": 100,
#                         "auto_ban_duration_minutes": 60,
#                     },
#                     "user_agent": {"enabled": True, "blocked_agents": []},
#                     "penetration": {
#                         "enabled": True,
#                         "log_suspicious": True,
#                         "suspicious_patterns": [],
#                     },
#                     "cors": {
#                         "enabled": True,
#                         "allow_origins": ["*"],
#                         "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#                         "allow_headers": ["*"],
#                         "allow_credentials": False,
#                         "max_age": 600,
#                     },
#                     "logging": {
#                         "enabled": True,
#                         "log_file": "pywebguard.log",
#                         "log_level": "INFO",
#                     },
#                     "storage": {
#                         "type": "memory",
#                         "redis_url": None,
#                         "redis_prefix": "pywebguard:",
#                         "ttl": 3600,
#                     },
#                 }

#                 with open(temp_file.name, "w") as f:
#                     json.dump(config, f)

#                 # Run the validate command
#                 with patch("sys.argv", ["pywebguard", "validate", temp_file.name]):
#                     with patch("builtins.print") as mock_print:
#                         assert main() == 0
#                         mock_print.assert_called_once()
#                         assert "valid" in mock_print.call_args[0][0]
#             finally:
#                 # Clean up
#                 os.unlink(temp_file.name)

#     def test_validate_command_invalid_file(self):
#         """Test the validate command with an invalid file."""
#         # Run the validate command with a non-existent file
#         with patch("sys.argv", ["pywebguard", "validate", "non_existent_file.json"]):
#             with patch("builtins.print") as mock_print:
#                 assert main() == 1
#                 mock_print.assert_called_once()
#                 assert "not found" in mock_print.call_args[0][0]

#     def test_validate_command_invalid_json(self):
#         """Test the validate command with invalid JSON."""
#         with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
#             try:
#                 # Create an invalid JSON file
#                 with open(temp_file.name, "w") as f:
#                     f.write("This is not valid JSON")

#                 # Run the validate command
#                 with patch("sys.argv", ["pywebguard", "validate", temp_file.name]):
#                     with patch("builtins.print") as mock_print:
#                         assert main() == 1
#                         mock_print.assert_called_once()
#                         assert "not valid JSON" in mock_print.call_args[0][0]
#             finally:
#                 # Clean up
#                 os.unlink(temp_file.name)

#     def test_test_connection_memory(self):
#         """Test the test connection command with memory storage."""
#         with patch("sys.argv", ["pywebguard", "test", "memory"]):
#             with patch("builtins.print") as mock_print:
#                 assert main() == 0
#                 mock_print.assert_called()
#                 assert "successful" in mock_print.call_args_list[-1][0][0]

#     @pytest.mark.skipif(
#         not hasattr(pytest, "importorskip"), reason="importorskip not available"
#     )
#     def test_test_connection_redis(self):
#         """Test the test connection command with Redis storage."""
#         # Mock Redis to avoid actual connection
#         with patch("pywebguard.cli.RedisStorage") as mock_redis:
#             mock_redis_instance = MagicMock()
#             mock_redis.return_value = mock_redis_instance

#             with patch("sys.argv", ["pywebguard", "test", "redis"]):
#                 with patch("builtins.print") as mock_print:
#                     assert main() == 0
#                     mock_print.assert_called()
#                     assert "successful" in mock_print.call_args_list[-1][0][0]

#     def test_ban_ip(self):
#         """Test the ban command."""
#         with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
#             try:
#                 # Create a valid config file
#                 config = {
#                     "ip_filter": {
#                         "enabled": True,
#                         "whitelist": [],
#                         "blacklist": [],
#                     },
#                     "rate_limit": {
#                         "enabled": True,
#                         "requests_per_minute": 60,
#                     },
#                     "storage": {
#                         "type": "memory",
#                     },
#                 }

#                 with open(temp_file.name, "w") as f:
#                     json.dump(config, f)

#                 # Run the ban command
#                 with patch(
#                     "sys.argv",
#                     [
#                         "pywebguard",
#                         "ban",
#                         temp_file.name,
#                         "192.168.1.1",
#                         "--duration",
#                         "30",
#                     ],
#                 ):
#                     with patch("builtins.print") as mock_print:
#                         with patch("pywebguard.cli.MemoryStorage.set") as mock_set:
#                             assert main() == 0
#                             mock_print.assert_called_once()
#                             assert "banned" in mock_print.call_args[0][0]
#                             mock_set.assert_called_once()
#                             assert mock_set.call_args[0][0] == "banned_ip:192.168.1.1"
#             finally:
#                 # Clean up
#                 os.unlink(temp_file.name)

#     def test_unban_ip(self):
#         """Test the unban command."""
#         with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
#             try:
#                 # Create a valid config file
#                 config = {
#                     "ip_filter": {
#                         "enabled": True,
#                         "whitelist": [],
#                         "blacklist": [],
#                     },
#                     "rate_limit": {
#                         "enabled": True,
#                         "requests_per_minute": 60,
#                     },
#                     "storage": {
#                         "type": "memory",
#                     },
#                 }

#                 with open(temp_file.name, "w") as f:
#                     json.dump(config, f)

#                 # Run the unban command
#                 with patch(
#                     "sys.argv", ["pywebguard", "unban", temp_file.name, "192.168.1.1"]
#                 ):
#                     with patch("builtins.print") as mock_print:
#                         with patch(
#                             "pywebguard.cli.MemoryStorage.exists", return_value=True
#                         ) as mock_exists:
#                             with patch(
#                                 "pywebguard.cli.MemoryStorage.delete"
#                             ) as mock_delete:
#                                 assert main() == 0
#                                 mock_print.assert_called_once()
#                                 assert "unbanned" in mock_print.call_args[0][0]
#                                 mock_exists.assert_called_once()
#                                 mock_delete.assert_called_once()
#                                 assert (
#                                     mock_delete.call_args[0][0]
#                                     == "banned_ip:192.168.1.1"
#                                 )
#             finally:
#                 # Clean up
#                 os.unlink(temp_file.name)

#     def test_status(self):
#         """Test the status command."""
#         with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
#             try:
#                 # Create a valid config file
#                 config = {
#                     "ip_filter": {
#                         "enabled": True,
#                         "whitelist": [],
#                         "blacklist": [],
#                     },
#                     "rate_limit": {
#                         "enabled": True,
#                         "requests_per_minute": 60,
#                     },
#                     "storage": {
#                         "type": "memory",
#                     },
#                 }

#                 with open(temp_file.name, "w") as f:
#                     json.dump(config, f)

#                 # Run the status command
#                 with patch("sys.argv", ["pywebguard", "status", temp_file.name]):
#                     with patch("builtins.print") as mock_print:
#                         assert main() == 0
#                         mock_print.assert_called()
#                         # Check that the version is printed
#                         assert any(
#                             "PyWebGuard v" in call[0][0]
#                             for call in mock_print.call_args_list
#                         )
#                         # Check that the storage type is printed
#                         assert any(
#                             "Storage: Memory" in call[0][0]
#                             for call in mock_print.call_args_list
#                         )
#             finally:
#                 # Clean up
#                 os.unlink(temp_file.name)

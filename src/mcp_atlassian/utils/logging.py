"""Logging utilities for MCP Atlassian.

This module provides enhanced logging capabilities for MCP Atlassian,
including level-dependent stream handling to route logs to the appropriate
output stream based on their level.
"""

import logging
import httpx
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()


def setup_logging(level: int = logging.WARNING) -> logging.Logger:
    """
    Configure MCP-Atlassian logging with level-based stream routing.

    Args:
        level: The minimum logging level to display (default: WARNING)

    Returns:
        The configured logger instance
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to prevent duplication
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add the level-dependent handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Configure specific loggers
    loggers = ["mcp-atlassian", "mcp.server", "mcp.server.lowlevel.server", "mcp-jira"]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

    # Return the application logger
    return logging.getLogger("mcp-atlassian")


def mask_sensitive(value: str | None, keep_chars: int = 4) -> str:
    """Masks sensitive strings for logging.

    Args:
        value: The string to mask
        keep_chars: Number of characters to keep visible at start and end

    Returns:
        Masked string with most characters replaced by asterisks
    """
    if not value:
        return "Not Provided"
    if len(value) <= keep_chars * 2:
        return "*" * len(value)
    return f"{value[:keep_chars]}{'*' * (len(value) - keep_chars * 2)}{value[-keep_chars:]}"


def log_config_param(
    logger: logging.Logger,
    service: str,
    param: str,
    value: str | None,
    sensitive: bool = False,
) -> None:
    """Logs a configuration parameter, masking if sensitive.

    Args:
        logger: The logger to use
        service: The service name (Jira or Confluence)
        param: The parameter name
        value: The parameter value
        sensitive: Whether the value should be masked
    """
    display_value = mask_sensitive(value) if sensitive else (value or "Not Provided")
    logger.info(f"{service} {param}: {display_value}")


async def log_tool_invocation(
    logger, tool_name, fetcher, response_data, execution_time
):
    """
    Sends the tool invocation log as a POST request to the n8n workflow endpoint.
    The log entry includes timestamp (UTC ISO8601), tool_name, user_details, and response_data.
    """
    from mcp_atlassian.confluence.client import ConfluenceClient
    from mcp_atlassian.jira.client import JiraClient

    user_details = {}
    try:
        if isinstance(fetcher, JiraClient):
            account_id = fetcher.get_current_user_account_id()
            user = fetcher.get_user_profile_by_identifier(account_id)
            user_details = user.to_simplified_dict()
        elif isinstance(fetcher, ConfluenceClient):
            # Assumes Confluence client has a method to get current user
            user_details = fetcher.get_current_user_info()
    except Exception as e:
        user_details = {"error": f"Failed to retrieve user details: {e}"}

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_name": tool_name,
        "user_details": user_details,
        "response_data": response_data,
        "execution_time_ms": execution_time,
    }

    endpoint = os.getenv("N8N_LOG_ENDPOINT")
    if not endpoint:
        logger.warning("N8N_LOG_ENDPOINT is not set in environment variables.")
        return
    try:
        async with httpx.AsyncClient() as client:
            await client.post(endpoint, json=log_entry, timeout=10)
    except Exception as e:
        logger.warning(f"Failed to send log entry to n8n: {e}")

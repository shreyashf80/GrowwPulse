"""Play Store Reviews MCP Server — stdio entrypoint."""

import logging

from mcp_servers.playstore_reviews.server import mcp

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mcp.run()

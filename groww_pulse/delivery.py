import json
import urllib.request
import urllib.error
import time
from functools import wraps
from typing import Dict, Any, List
from .renderer import EmailPayload

BASE_URL = "https://shreyash-mcp-server-production-5d26.up.railway.app"

def retry(times=3, delay=1, backoff=2):
    """Simple retry decorator with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            mtries, mdelay = times, delay
            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    import click
                    click.secho(f"Warning in {func.__name__}: {e}. Retrying in {mdelay}s...", fg="yellow")
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return func(*args, **kwargs)
        return wrapper
    return decorator

@retry(times=3, delay=1, backoff=2)
def deliver_to_docs(content: str, doc_id: str) -> Dict[str, Any]:
    """
    Sends the rendered plain text content to the Google Docs API
    via the custom Railway Remote Delivery Server.
    """
    url = f"{BASE_URL}/append_to_doc"
    payload = {
        "doc_id": doc_id,
        "content": content
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body)
    except urllib.error.URLError as e:
        if hasattr(e, 'read'):
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"Failed to deliver to Google Docs: {e} - {err_body}")
        raise RuntimeError(f"Failed to deliver to Google Docs: {e}")

@retry(times=3, delay=1, backoff=2)
def deliver_to_gmail(email_payload: EmailPayload, recipients: List[str]) -> Dict[str, Any]:
    """
    Creates a Gmail draft with the rendered HTML body
    via the custom Railway Remote Delivery Server.
    """
    url = f"{BASE_URL}/create_email_draft"
    to_str = ", ".join(recipients)
    
    payload = {
        "to": to_str,
        "subject": email_payload.subject,
        "body": email_payload.html_body
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body)
    except urllib.error.URLError as e:
        if hasattr(e, 'read'):
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"Failed to deliver to Gmail: {e} - {err_body}")
        raise RuntimeError(f"Failed to deliver to Gmail: {e}")

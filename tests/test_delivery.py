"""Tests for the delivery module."""

import json
import pytest
from unittest.mock import patch, MagicMock
from groww_pulse.delivery import deliver_to_docs, deliver_to_gmail
from groww_pulse.renderer import EmailPayload

def test_deliver_to_docs_success():
    mock_response = MagicMock()
    # Mock context manager behavior for urlopen
    mock_response.__enter__.return_value = mock_response
    mock_response.read.return_value = b'{"status": "ok", "doc_id": "test1234"}'
    
    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        result = deliver_to_docs("Hello World", "test1234")
        
        assert result == {"status": "ok", "doc_id": "test1234"}
        
        # Verify the request
        req = mock_urlopen.call_args[0][0]
        assert req.full_url == "https://shreyash-mcp-server-production-5d26.up.railway.app/append_to_doc"
        assert req.method == "POST"
        
        # Verify payload
        payload = json.loads(req.data.decode("utf-8"))
        assert payload["doc_id"] == "test1234"
        assert payload["content"] == "Hello World"

def test_deliver_to_gmail_success():
    mock_response = MagicMock()
    # Mock context manager behavior for urlopen
    mock_response.__enter__.return_value = mock_response
    mock_response.read.return_value = b'{"status": "drafted"}'
    
    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        email = EmailPayload(
            subject="Test Subject",
            html_body="<p>Test HTML</p>",
            text_body="Test Text",
            doc_link="https://docs.google.com/test"
        )
        
        result = deliver_to_gmail(email, ["a@test.com", "b@test.com"])
        
        assert result == {"status": "drafted"}
        
        # Verify the request
        req = mock_urlopen.call_args[0][0]
        assert req.full_url == "https://shreyash-mcp-server-production-5d26.up.railway.app/create_email_draft"
        assert req.method == "POST"
        
        # Verify payload
        payload = json.loads(req.data.decode("utf-8"))
        assert payload["to"] == "a@test.com, b@test.com"
        assert payload["subject"] == "Test Subject"
        assert payload["body"] == "<p>Test HTML</p>"

def test_deliver_to_docs_failure():
    import urllib.error
    
    mock_error = urllib.error.URLError("Connection refused")
    
    with patch("urllib.request.urlopen", side_effect=mock_error):
        with pytest.raises(RuntimeError, match="Failed to deliver to Google Docs"):
            deliver_to_docs("Hello World", "test1234")

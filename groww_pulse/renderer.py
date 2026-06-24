"""Groww Pulse — Report rendering (Google Docs payload + email HTML)."""

from dataclasses import dataclass
from typing import Any, Dict, List

from groww_pulse.config import Config


@dataclass
class EmailPayload:
    subject: str
    html_body: str
    text_body: str
    doc_link: str


def render_docs_payload(themes: List[Dict[str, Any]], iso_week: str, config: Config) -> str:
    """Generate a plain text payload for Google Docs.
    
    The Google Docs MCP server currently only supports appending raw text, 
    so we return the unformatted text block.
    """
    # Heading
    heading = f"{config.product.name} — Weekly Review Pulse ({iso_week})\n\n"
    
    # Metadata
    metadata = f"Period: {config.ingestion.window_weeks} weeks ending {iso_week}\n\n"
    
    content = heading + metadata
    
    for i, theme in enumerate(themes, 1):
        name = theme.get("theme_name", "Unknown Theme")
        count = theme.get("review_count", 0)
        avg_rating = theme.get("avg_rating", 0.0)
        desc = theme.get("description", "")
        
        content += f"{i}. {name} ({count} reviews, Avg Rating: {avg_rating})\n"
        content += f"   {desc}\n\n"
        
        # Quotes
        quotes = theme.get("quotes", [])
        if quotes:
            content += "   Real User Quotes:\n"
            for q in quotes:
                text = q.get("text", "")
                rating = q.get("rating", "?")
                content += f"   > \"{text}\" ({rating}/5)\n"
            content += "\n"
            
        # Actions
        actions = theme.get("action_ideas", [])
        if actions:
            content += "   Action Ideas:\n"
            for a in actions:
                title = a.get("title", "")
                detail = a.get("detail", "")
                content += f"   - {title}: {detail}\n"
            content += "\n"
            
    content += "---\n\n"
    
    return content


def render_email_payload(themes: List[Dict[str, Any]], iso_week: str, config: Config, doc_id: str = "") -> EmailPayload:
    """Generate HTML and plain text email bodies."""
    
    subject = f"{config.product.name} Review Pulse — {iso_week}"
    
    doc_link = f"https://docs.google.com/document/d/{doc_id}" if doc_id else "https://docs.google.com/"
    
    # Plain text
    text_lines = [
        f"Hi Team,\n",
        f"Here are the top themes from our {config.product.name} user reviews for {iso_week}:\n"
    ]
    for theme in themes:
        name = theme.get("theme_name", "Unknown Theme")
        count = theme.get("review_count", 0)
        text_lines.append(f"- {name} ({count} reviews)")
        
    text_lines.append(f"\nRead full report → {doc_link}")
    text_body = "\n".join(text_lines)
    
    # HTML
    html_lines = [
        f"<p>Hi Team,</p>",
        f"<p>Here are the top themes from our {config.product.name} user reviews for <strong>{iso_week}</strong>:</p>",
        "<ul>"
    ]
    for theme in themes:
        name = theme.get("theme_name", "Unknown Theme")
        count = theme.get("review_count", 0)
        html_lines.append(f"  <li><strong>{name}</strong> ({count} reviews)</li>")
        
    html_lines.append("</ul>")
    html_lines.append(f'<p><a href="{doc_link}">Read full report &rarr;</a></p>')
    html_body = "\n".join(html_lines)
    
    return EmailPayload(
        subject=subject,
        html_body=html_body,
        text_body=text_body,
        doc_link=doc_link
    )

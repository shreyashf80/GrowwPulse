"""
Groww Pulse — CLI entrypoint.

Usage:
    python -m groww_pulse run [OPTIONS]
    python -m groww_pulse run --help
"""

from __future__ import annotations

import sys
import os
from datetime import datetime, timezone
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import click

from groww_pulse import __version__
from groww_pulse.config import Config, apply_cli_overrides, load_config

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _current_iso_week() -> str:
    """Return the current ISO week as ``YYYY-WNN`` (e.g. ``2026-W24``)."""
    now = datetime.now(tz=timezone.utc)
    iso = now.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def _validate_iso_week(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Validate that *value* is a well-formed ISO week string."""
    import re

    if not re.match(r"^\d{4}-W\d{2}$", value):
        raise click.BadParameter(
            f"Invalid ISO week format: '{value}'. Expected YYYY-WNN (e.g. 2026-W24)."
        )
    # Verify it's a real week
    try:
        year, week = int(value[:4]), int(value[6:])
        datetime.strptime(f"{year} {week} 1", "%G %V %u")
    except ValueError:
        raise click.BadParameter(f"ISO week '{value}' does not exist.")
    return value


def _print_banner(config: Config, week: str, dry_run: bool, draft_only: bool) -> None:
    """Print a startup banner with run parameters."""
    click.secho("=" * 60, fg="cyan")
    click.secho(f"  Groww Review Pulse  v{__version__}", fg="cyan", bold=True)
    click.secho("=" * 60, fg="cyan")
    click.echo()
    click.echo(f"  Product      : {config.product.name}")
    click.echo(f"  App ID       : {config.product.play_store_app_id}")
    click.echo(f"  ISO Week     : {week}")
    click.echo(f"  Window       : {config.ingestion.window_weeks} weeks")
    click.echo(f"  Max reviews  : {config.ingestion.max_reviews}")
    click.echo(f"  LLM model    : {config.llm.model}")
    click.echo(f"  Dry-run      : {'Yes' if dry_run else 'No'}")
    click.echo(f"  Draft-only   : {'Yes' if draft_only else 'No'}")
    click.echo()
    click.secho("-" * 60, fg="cyan")
    click.echo()


# ---------------------------------------------------------------------------
# Frontend export helper
# ---------------------------------------------------------------------------


def _export_frontend_output(
    themes: list,
    reviews: list,
    iso_week: str,
    config,
    token_usage: dict,
    docs_payload: str = "",
    email_payload=None,
) -> None:
    """Write data/frontend_output.json in the Phase-6 contract schema."""
    import json
    from collections import Counter
    from pathlib import Path

    # Rating distribution (percentage, rounded)
    counts: Counter = Counter(r.rating for r in reviews)
    total = len(reviews) or 1
    dist = {str(star): round((counts[star] / total) * 100) for star in [5, 4, 3, 2, 1]}

    # Avg rating across all reviews
    avg_rating = round(sum(r.rating for r in reviews) / total, 1) if reviews else 0.0

    # Build theme list in frontend schema
    ranked_themes = []
    for idx, t in enumerate(themes, 1):
        ranked_themes.append({
            "rank": idx,
            "theme_name": t.get("theme_name", "Unknown"),
            "review_count": t.get("review_count", 0),
            "avg_rating": round(float(t.get("avg_rating", 0)), 2),
            "description": t.get("description", ""),
            "quotes": [
                {"text": q.get("text", ""), "rating": q.get("rating", 0)}
                for q in t.get("quotes", [])
            ],
            "action_ideas": [
                {"title": a.get("title", ""), "detail": a.get("detail", "")}
                for a in t.get("action_ideas", [])
            ],
        })

    doc_id = config.delivery.google_doc_id
    doc_url = f"https://docs.google.com/document/d/{doc_id}" if doc_id else ""

    payload = {
        "iso_week": iso_week,
        "window_weeks": config.ingestion.window_weeks,
        "reviews_ingested": len(reviews),
        "avg_rating": avg_rating,
        "themes": ranked_themes,
        "rating_distribution": dist,
        "pipeline": {
            "model": config.llm.model,
            "llm_tokens_used": token_usage.get("total_tokens", 0),
            "llm_tokens_limit": 100_000,
            "doc_status": "dry_run",
            "gmail_status": "dry_run",
            "doc_url": doc_url,
            "run_id": iso_week,
            "run_timestamp": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
        },
        "email": {
            "subject": email_payload.subject if email_payload else "",
            "text_body": email_payload.text_body if email_payload else "",
            "html_body": email_payload.html_body if email_payload else "",
            "doc_link": email_payload.doc_link if email_payload else doc_url,
        },
        "docs_report": docs_payload,
    }

    # Write to project data/ dir
    out_path = Path("data") / "frontend_output.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # Also write to the Next.js public/data/ so the dev server picks it up immediately
    nextjs_pub = Path(__file__).resolve().parent.parent / "frontend-next" / "public" / "data"
    nextjs_pub.mkdir(parents=True, exist_ok=True)
    with open(nextjs_pub / "frontend_output.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    click.secho(f"✓ Frontend output written → {out_path} + frontend-next/public/data/", fg="green", bold=True)


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------


@click.group()
@click.version_option(version=__version__, prog_name="groww-pulse")
def cli() -> None:
    """Groww Review Pulse — automated weekly insight reports from Google Play reviews."""


# ---------------------------------------------------------------------------
# `run` command
# ---------------------------------------------------------------------------


@cli.command()
@click.option(
    "--week",
    default=None,
    callback=lambda ctx, param, val: _validate_iso_week(ctx, param, val) if val else val,
    help="ISO week to generate report for (e.g. 2026-W24). Defaults to current week.",
)
@click.option(
    "--window",
    type=int,
    default=None,
    help="Rolling window in weeks for review ingestion. Overrides config.yaml.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Run the full pipeline but skip delivery (no Doc/Gmail writes).",
)
@click.option(
    "--draft-only",
    is_flag=True,
    default=False,
    help="Create Gmail draft but do not send.",
)
@click.option(
    "--export-frontend",
    is_flag=True,
    default=False,
    help="Write data/frontend_output.json after summarization (for the web dashboard).",
)
@click.option(
    "--config",
    "config_path",
    default=None,
    type=click.Path(exists=True),
    help="Path to config.yaml. Defaults to project root.",
)
def run(
    week: str | None,
    window: int | None,
    dry_run: bool,
    draft_only: bool,
    export_frontend: bool,
    config_path: str | None,
) -> None:
    """Run the weekly review pulse pipeline."""
    # --- Check Python version ---
    if sys.version_info < (3, 9):
        click.secho(
            f"ERROR: Python >= 3.9 required. Found: {sys.version}",
            fg="red",
            err=True,
        )
        sys.exit(1)

    # --- Resolve ISO week ---
    if week is None:
        week = _current_iso_week()

    # --- Load config ---
    config = load_config(config_path)
    config = apply_cli_overrides(config, window=window, draft_only=draft_only)

    # --- Print banner ---
    _print_banner(config, week, dry_run, draft_only)

    import asyncio
    import json
    from groww_pulse.ingestion import ingest_reviews
    from groww_pulse.clustering import NormalizedReview, run_clustering_pipeline
    from groww_pulse.summarizer import run_summarization_pipeline
    import pprint
    from dataclasses import asdict

    async def _run_async():
        click.echo("  [*] 1. Ingest reviews & 2. PII scrubbing")
        reviews = await ingest_reviews(config)
        if not reviews:
            click.secho("No reviews found within the window. Aborting pipeline.", fg="yellow", err=True)
            return
            
        normalized = [
            NormalizedReview(
                doc_id=f"doc_{i}",
                rating=r.rating,
                text=r.text,
                thumbs_up=r.thumbs_up,
                app_version=r.app_version,
            )
            for i, r in enumerate(reviews)
        ]
        
        click.echo("  [*] 3. Clustering (UMAP + HDBSCAN)")
        clusters = run_clustering_pipeline(normalized, config)
        if not clusters:
            click.secho("No clusters generated.", fg="yellow")
            return
            
        click.echo("  [*] 4. LLM summarization")
        themes, token_usage = await run_summarization_pipeline(clusters, config)
        
        # 5. Load / Create Receipt
        from groww_pulse.receipts import RunReceipt, load_receipt, save_receipt
        from datetime import datetime, timezone
        
        receipt = load_receipt(config.receipts.storage_path, week)
        if not receipt:
            receipt = RunReceipt(
                idempotency_key=f"groww:{week}",
                run_timestamp=datetime.now(timezone.utc).isoformat(),
                review_window={},
                reviews_ingested=len(reviews),
                clusters_found=len(clusters),
                themes_generated=len(themes),
                llm_usage=token_usage
            )
            # Save initial state
            save_receipt(config.receipts.storage_path, week, receipt)

        # 6. Save JSON Themes
        from pathlib import Path
        receipts_dir = Path(config.receipts.storage_path)
        receipts_dir.mkdir(parents=True, exist_ok=True)
        themes_path = receipts_dir / f"{week}_themes.json"
        
        with open(themes_path, "w", encoding="utf-8") as f:
            json.dump(themes, f, indent=2)
            
        click.secho(f"\nSaved structured JSON themes to: {themes_path}", fg="green")
        
        # 7. Report Rendering & Delivery
        click.secho("  [*] 6. Report rendering", fg="cyan", bold=True)
        from groww_pulse.renderer import render_docs_payload, render_email_payload
        docs_payload = render_docs_payload(themes, week, config)
        email_payload = render_email_payload(themes, week, config, config.delivery.google_doc_id)
        
        if dry_run:
            click.secho("\n--- Dry Run: Docs Payload ---", fg="cyan", bold=True)
            click.echo(docs_payload)
            
            click.secho("\n--- Dry Run: Email HTML Body ---", fg="cyan", bold=True)
            click.echo(email_payload.html_body)
            
            click.secho(f"\nToken usage: {token_usage}", fg="yellow")

            if export_frontend:
                _export_frontend_output(themes, reviews, week, config, token_usage,
                                        docs_payload=docs_payload, email_payload=email_payload)

            click.secho("\n\u2713 Render complete (dry-run). No delivery attempted.\n", fg="green", bold=True)
        else:
            from groww_pulse.delivery import deliver_to_docs, deliver_to_gmail
            
            click.secho("\n--- Delivering to Google Docs ---", fg="cyan", bold=True)
            if receipt.delivery.google_doc.status == "appended":
                click.secho(f"\u2713 Skipped Docs append (already appended with ID: {receipt.delivery.google_doc.doc_id})", fg="blue")
            else:
                try:
                    docs_res = deliver_to_docs(docs_payload, config.delivery.google_doc_id)
                    click.secho(f"\u2713 Docs append successful: {docs_res}", fg="green")
                    receipt.delivery.google_doc.status = "appended"
                    receipt.delivery.google_doc.doc_id = config.delivery.google_doc_id
                    save_receipt(config.receipts.storage_path, week, receipt)
                except Exception as e:
                    click.secho(f"\u2717 Docs delivery failed: {e}", fg="red", err=True)
                    receipt.delivery.google_doc.status = "failed"
                    save_receipt(config.receipts.storage_path, week, receipt)
                    return
                
            click.secho("\n--- Delivering to Gmail ---", fg="cyan", bold=True)
            if receipt.delivery.gmail.status == "drafted":
                click.secho(f"\u2713 Skipped Gmail draft (already drafted with ID: {receipt.delivery.gmail.draft_id})", fg="blue")
            else:
                try:
                    gmail_res = deliver_to_gmail(email_payload, config.delivery.email_recipients)
                    click.secho(f"\u2713 Gmail draft created: {gmail_res}", fg="green")
                    receipt.delivery.gmail.status = "drafted"
                    receipt.delivery.gmail.draft_id = gmail_res.get("draft_id", "unknown")
                    save_receipt(config.receipts.storage_path, week, receipt)
                except Exception as e:
                    click.secho(f"\u2717 Gmail delivery failed: {e}", fg="red", err=True)
                    receipt.delivery.gmail.status = "failed"
                    save_receipt(config.receipts.storage_path, week, receipt)
                    return
                
            click.secho(f"\nToken usage: {token_usage}", fg="yellow")

            if export_frontend:
                _export_frontend_output(themes, reviews, week, config, token_usage,
                                        docs_payload=docs_payload, email_payload=email_payload)
            
            click.secho("\n" + "=" * 60, fg="cyan", bold=True)
            click.secho(f"  Groww Review Pulse Run Summary: {week}", fg="cyan", bold=True)
            click.secho("=" * 60, fg="cyan", bold=True)
            click.echo(f"  Reviews ingested : {receipt.reviews_ingested}")
            click.echo(f"  Clusters found   : {receipt.clusters_found}")
            click.echo(f"  Themes generated : {receipt.themes_generated}")
            click.echo(f"  Google Docs      : {receipt.delivery.google_doc.status}")
            click.echo(f"  Gmail            : {receipt.delivery.gmail.status}")
            click.secho("=" * 60, fg="cyan", bold=True)
            click.secho("\n\u2713 Full pipeline run and delivery completed successfully!\n", fg="green", bold=True)

    asyncio.run(_run_async())


@cli.command()
@click.option("--week", default=None, help="ISO week to check status for (e.g. 2026-W24).")
@click.option("--all", "all_receipts", is_flag=True, default=False, help="List all receipts.")
@click.option("--config", "config_path", default=None, type=click.Path(exists=True), help="Path to config.yaml.")
def status(week: str | None, all_receipts: bool, config_path: str | None) -> None:
    """Check the status of previous pipeline runs."""
    config = load_config(config_path)
    from pathlib import Path
    import json
    from groww_pulse.receipts import load_receipt
    
    storage_path = Path(config.receipts.storage_path)
    
    if all_receipts:
        if not storage_path.exists():
            click.secho("No receipts found.", fg="yellow")
            return
            
        receipts = list(storage_path.glob("groww_*.json"))
        if not receipts:
            click.secho("No receipts found.", fg="yellow")
            return
            
        click.secho("=== All Run Receipts ===", fg="cyan", bold=True)
        for r_path in sorted(receipts):
            try:
                with open(r_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                click.echo(f"- {data.get('idempotency_key')} | Docs: {data.get('delivery', {}).get('google_doc', {}).get('status')} | Gmail: {data.get('delivery', {}).get('gmail', {}).get('status')}")
            except Exception as e:
                click.secho(f"Failed to read {r_path}: {e}", fg="red")
    else:
        if week is None:
            week = _current_iso_week()
            
        receipt = load_receipt(str(storage_path), week)
        if not receipt:
            click.secho(f"No receipt found for week {week}.", fg="yellow")
            return
            
        click.secho(f"=== Receipt for {week} ===", fg="cyan", bold=True)
        import pprint
        pprint.pprint(receipt.to_dict())

# ---------------------------------------------------------------------------
# Module entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()

# Groww Review Pulse

Automated weekly **"pulse"** that turns public Google Play Store reviews for **Groww** into a one-page insight report, delivered to stakeholders via Google Workspace using MCP (Model Context Protocol), and visualized in a sleek Next.js dashboard.

## Overview

The pipeline executes the following stages:
1. **Ingestion**: Scrapes recent reviews from the Google Play Store (via MCP).
2. **Scrubbing**: Automatically redacts Personally Identifiable Information (PII).
3. **Clustering**: Uses BGE embeddings, UMAP, and HDBSCAN to group reviews into semantic clusters.
4. **Summarization**: Utilizes Groq (Llama 3) to summarize clusters into top actionable themes.
5. **Delivery**: Appends a report to a shared Google Doc and drafts a summary email via Gmail (via MCP).
6. **Frontend**: Generates a structured JSON file consumed by a modern Next.js dashboard.

## Quick Start

### Prerequisites

- Node.js ≥ 18
- Python ≥ 3.11
- `pip` (or `uv`)
- Groq API Key (for summarization)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shreyashf80/GrowwPulse.git
   cd GrowwPulse
   ```

2. **Backend Setup (Python)**
   ```bash
   # Create a virtual environment
   python -m venv .venv
   source .venv/bin/activate

   # Install the package and dependencies
   pip install -e ".[dev]"
   pip install python-dotenv groq
   ```

3. **Frontend Setup (Next.js)**
   ```bash
   cd frontend-next
   npm install
   ```

### Configuration

1. **Environment Variables**
   Create a `.env` file at the root of the project with your Groq API key:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   ```

2. **Pipeline Configuration**
   Edit `config.yaml` at the project root. Key fields:
   - `delivery.google_doc_id` — ID of the target Google Doc
   - `delivery.email_recipients` — list of stakeholder email addresses

### Running the Pipeline (CLI)

```bash
# Show help
python -m groww_pulse run --help

# Run for the current week (dry-run — no delivery)
python -m groww_pulse run --dry-run

# Run and export data for the frontend dashboard
python -m groww_pulse run --week 2026-W24 --dry-run --export-frontend
```

### Running the Dashboard

Start the Next.js development server:
```bash
cd frontend-next
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser. The dashboard allows you to:
- View Hero statistics and top themes.
- Trigger pipeline regeneration directly from the sidebar.
- Open the Google Doc report.
- Preview the generated email draft.

## Project Structure

```
Groww_Pulse/
├── docs/                    # Problem statement, architecture, implementation plan
├── mcp_servers/             # In-repo MCP servers (Play Store scraper)
├── frontend-next/           # Next.js App Router dashboard
├── groww_pulse/             # Main Python application package
│   ├── __main__.py          # CLI entrypoint
│   ├── config.py            # Config loader
│   ├── ingestion.py         # Review fetching + PII scrubbing
│   ├── clustering.py        # UMAP + HDBSCAN pipeline
│   ├── summarizer.py        # LLM theme extraction via Groq
│   ├── renderer.py          # Report rendering (Docs + email)
│   └── delivery.py          # MCP-based delivery
├── tests/                   # Python test suite
├── config.yaml              # Runtime configuration
└── pyproject.toml           # Python project metadata
```

## Documentation

- [Problem Statement](docs/problemStatement.md)
- [Architecture](docs/architecture.md)
- [Implementation Plan](docs/implementation-plan.md)

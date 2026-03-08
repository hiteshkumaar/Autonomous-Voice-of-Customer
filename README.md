# Autonomous Voice of Customer Agent

An autonomous NLP + LLM-ready agent for weekly e-commerce review intelligence.

## What this delivers
- Agent-driven ingestion of public reviews (Amazon/Flipkart URL scraping).
- Weekly automation (GitHub Actions cron + local scheduler script).
- Incremental capture (new reviews only, dedup by `product_id + review_id`).
- Sentiment + thematic tagging.
- Two reports:
  - `outputs/global_action_items.md`
  - `outputs/weekly_delta_action_items.md`
- Delta proof logs: `outputs/delta_sample_<run_id>.csv`
- Grounded conversational querying from SQLite.

## Stack
- Python 3.10+
- SQLite
- CSV seeds for deterministic demo
- Optional ClawdBot/OpenClaw API for LLM classification

## Project structure
- `voc_agent/pipeline.py`: weekly ingestion + NLP + reporting flow
- `voc_agent/tools/scraper.py`: URL scraping and CSV fallback
- `voc_agent/tools/nlp.py`: sentiment + theme tagging (LLM + rule fallback)
- `voc_agent/tools/storage.py`: run tracking and incremental persistence
- `voc_agent/tools/reports.py`: global/weekly action report generation
- `voc_agent/tools/query.py`: grounded Q&A helpers
- `clawdbot_agent.py`: function-calling style agent wrapper
- `run_scheduler.py`: local weekly scheduler
- `scripts/demo_two_runs.py`: demo initial + delta run proof

## Setup
```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

If `python --version` says Python was not found on Windows, use one of these:
```powershell
py -3.10 --version
where.exe python
```
If `py -3.10` works, create venv with:
```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python --version
```
Also disable Microsoft Store alias:
`Settings -> Apps -> Advanced app settings -> App execution aliases -> turn OFF python.exe/python3.exe`

Optional `.env` values for LLM:
- `CLAWDBOT_API_KEY`
- `CLAWDBOT_BASE_URL`
- `CLAWDBOT_MODEL`

OpenAI-compatible aliases are also supported:
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL` (default: `https://api.openai.com/v1`)
- `OPENAI_MODEL` (default: `gpt-4o-mini`)

Without these, classifier uses deterministic rule-based fallback.

### Where to get ClawdBot/OpenClaw API values
- `CLAWDBOT_API_KEY`: generate from your ClawdBot/OpenClaw account dashboard (API keys section).
- `CLAWDBOT_BASE_URL`: your provider's API base endpoint.
- `CLAWDBOT_MODEL`: model id enabled for your account.

Set in `.env`:
```env
CLAWDBOT_API_KEY=your_key
CLAWDBOT_BASE_URL=https://your-provider-endpoint
CLAWDBOT_MODEL=your-model-id
```

## Run the pipeline
Use seed data (recommended for assignment demo):
```bash
python -m voc_agent.pipeline --seed
```

Run live scraping:
```bash
python -m voc_agent.pipeline
```

This creates:
- `data/voc_reviews.db`
- `outputs/global_action_items.md`
- `outputs/weekly_delta_action_items.md`
- `outputs/delta_sample_<run_id>.csv`

## Prove weekly delta handling
```bash
python scripts/demo_two_runs.py
```
This runs ingestion twice, appends new sample reviews between runs, and produces a second delta report/log showing newly captured rows only.

## Conversational querying (grounded)
```bash
python chat_cli.py
```
Example prompt equivalent:
- Compare `master_buds_1` vs `master_buds_max` on themes `Comfort/Fit, ANC`

## Unit tests
Run all tests:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
Included tests:
- `tests/test_nlp.py`: sentiment + theme tagging
- `tests/test_reports.py`: markdown report generation
- `tests/test_query.py`: grounded comparison behavior

## Autonomous scheduler options
### GitHub Actions
Workflow file: `.github/workflows/weekly.yml`
- Cron: Sunday 02:00 UTC
- Manual trigger supported via `workflow_dispatch`

### Local scheduler
```bash
python run_scheduler.py
```

## Proactive action push (optional)
To proactively send weekly action items to team channels, configure incoming webhook URLs in `.env`:
- `PRODUCT_TEAM_WEBHOOK_URL`
- `MARKETING_TEAM_WEBHOOK_URL`
- `SUPPORT_TEAM_WEBHOOK_URL`

When set, each successful run posts team-specific action bullets extracted from weekly/global reports.
Set `NOTIFY_ON_ZERO_DELTA=true` if you want notifications even when no new reviews were captured.

## Deployment on Render
Yes, you can deploy on Render.

Recommended approach:
1. Create a **Background Worker** for scheduled ingestion (`python run_scheduler.py`), or use Render Cron Job to run `python -m voc_agent.pipeline` weekly.
2. Add environment variables in Render dashboard:
   - `CLAWDBOT_API_KEY`
   - `CLAWDBOT_BASE_URL`
   - `CLAWDBOT_MODEL`
   - `PRODUCT_CONFIG_PATH=data/products.json`
   - `DB_PATH=data/voc_reviews.db`
   - `OUTPUT_DIR=outputs`
3. Persistent disk:
   - Attach a disk and point DB/outputs to disk-backed paths, otherwise SQLite data resets on redeploy.
4. If you want chat/query as web API, add a small FastAPI wrapper and deploy as Web Service.

## Data privacy compliance
- Pipeline is designed for public review URLs only.
- No proprietary/internal data is required or used.

## Notes for production hardening
- Add robust anti-bot compliant data source (official API or approved scraper).
- Add pagination + retries + proxy rotation if policy permits.
- Add SQL-level indexing and query tests for scale.
- Add unit/integration tests and CI checks.

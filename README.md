[**فارسی**](README.fa.md) | **English**

# Better Config Collector

A production-grade, curated V2Ray/VLESS/Trojan/ShadowSocks subscription aggregator.

**Philosophy:** This is NOT a giant config dump. It's a lightweight, curated subscription generator that collects, deduplicates, scores, and publishes only high-quality configs.

## Features

- Collects configs from public Telegram channels, GitHub repos, and subscription URLs
- Parses vmess://, vless://, trojan://, and ss://
- Deduplicates intelligently (by protocol + host + port + credentials + transport)
- Scores configs (Reality +25, Cloudflare +20, TLS +15, etc.)
- Runs lightweight TCP health checks (3s timeout, async)
- Generates 6 categorized outputs: mix, cloudflare, reality, mobile, fast, clean
- Outputs raw .txt, base64, and optional Clash YAML
- Fully async (asyncio + httpx + telethon)
- No database — lightweight JSON file cache
- Easy deployment: GitHub Actions, Docker, VPS cron

## Architecture

```
app/
  collectors/       # Telegram, GitHub, subscription URL collectors
  extractors/       # Regex link extraction
  parsers/          # vmess, vless, trojan, shadowsocks parsers
  normalizers/      # Config normalization (hostnames, transport, etc.)
  scoring/          # Scoring engine
  health/           # Async TCP health checker
  filters/          # Category filters (mix, cf, reality, mobile, fast, clean)
  outputs/          # Raw, base64, Clash YAML generators
  models/           # Pydantic ProxyConfig model
  utils/            # Logger, retry, cache
  pipeline.py       # Pipeline orchestrator
  sources.py        # Source loaders
config/             # Configuration files
generated/          # Output subscriptions
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Add sources (see below)
# Then run
python main.py
```

## Adding Sources

### Telegram Channels

Edit `config/telegram_channels.txt`:

```
@freev2ray
@proxy_channel
```

Requires TG_API_ID and TG_API_HASH from https://my.telegram.org.

### GitHub / Raw URLs

Edit `config/github_sources.json`:

```json
[
  {
    "name": "my-source",
    "url": "https://raw.githubusercontent.com/user/repo/main/configs.txt",
    "type": "raw"
  }
]
```

### Subscription URLs

Edit `config/subscription_sources.txt`:

```
https://example.com/subscription
https://another.example.com/config
```

Auto-detects base64-encoded subscriptions.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TG_API_ID` | For Telegram | Telegram API ID (https://my.telegram.org) |
| `TG_API_HASH` | For Telegram | Telegram API hash |
| `TG_SESSION` | No | Telethon session name (default: anon) |
| `GITHUB_TOKEN` | No | GitHub token for higher rate limits |

## Deployment

### GitHub Actions

1. Fork this repository
2. Add `TG_API_ID` and `TG_API_HASH` to GitHub Secrets
3. The workflow runs every 10 minutes automatically

### Docker

```bash
docker-compose up -d
```

### VPS Cron

```bash
# Run every 10 minutes
*/10 * * * * cd /path/to/config-collector && python3 main.py >> /var/log/collector.log 2>&1
```

## Outputs

After running, `generated/` contains:

| File | Description | Max Configs |
|------|-------------|-------------|
| `mix.txt` | Best overall configs | 300 |
| `cloudflare.txt` | Cloudflare CDN only | 150 |
| `reality.txt` | Reality/XTLS/Vision only | 100 |
| `mobile.txt` | Mobile-friendly | 100 |
| `fast.txt` | Top scored | 50 |
| `clean.txt` | Clean configs | 100 |
| `base64/*.txt` | Base64 encoded versions | same |

## Configuration

See `config/settings.yaml` for all settings:

- Output limits per category
- Timeouts (HTTP, TCP)
- Health check concurrency
- Source toggles
- Retry settings
- Logging level/format
- Output format toggles (raw, base64, clash)

## License

MIT

#!/usr/bin/env python3
"""Generate Mintlify mdx pages from swell_data_catalog.json for surf-doc."""

import json
import re
from pathlib import Path
from collections import defaultdict

CATALOG_PATH = Path(__file__).parent.parent.parent / "swell" / "data-catalog" / "data" / "swell_data_catalog.json"
OUTPUT_DIR = Path(__file__).parent.parent / "data-catalog"


CATEGORY_DESCRIPTIONS = {
    "DEX Trades": "Enriched swap events across 6 chains with token symbols, USD amounts, and protocol attribution.",
    "Prices": "Daily token prices combining CoinGecko data and DEX VWAP calculations.",
    "Token Metadata": "ERC-20 contract registry mapping addresses to symbols, names, and decimals.",
    "Transfers": "ERC-20 and native token transfers enriched with symbols and USD pricing.",
    "TVL / Fees / Yields": "Protocol-level daily aggregates for total value locked, fee revenue, and yield rates.",
    "Lending & Staking": "Protocol-level daily activity aggregates for lending and staking protocols.",
    "Bridges": "Cross-chain bridge volume aggregated daily.",
    "Prediction Markets": "Polymarket, Kalshi, and cross-platform prediction market data — trades, market details, prices, volume, and open interest.",
    "Hyperliquid": "Perpetual futures market data, funding rates, and contract metadata from Hyperliquid L1.",
    "Chain Metrics": "Daily chain-level aggregates including transaction counts, active addresses, gas usage, and contract deployments.",
    "Curated Analytics": "Dashboard-ready pre-computed analytics — whale trades, hot markets, leaderboards, and daily reports.",
}


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def format_type(col_type: str) -> str:
    """Shorten ClickHouse types for display."""
    return col_type.replace("Nullable(", "Nullable(").replace("LowCardinality(", "")


def generate_overview(catalog: dict) -> str:
    total = catalog["total_tables"]
    cats = catalog["categories"]
    practices = catalog["query_best_practices"]
    entity_links = catalog["entity_linking"]
    freshness = catalog.get("data_freshness", {})

    lines = [
        '---',
        'title: "Data Catalog"',
        f'description: "{total} analyst-ready ClickHouse tables for crypto data analysis"',
        '---',
        '',
        f'> **{total} tables** across {len(cats)} categories, available via a readonly ClickHouse account.',
        '',
        'The Surf Data Catalog documents all tables available to agents and analysts. Tables are organized into categories and exposed as ClickHouse views in the `agent` and `curated` databases.',
        '',
        '## Connection',
        '',
        '| Setting | Value |',
        '|---------|-------|',
        '| **Protocol** | ClickHouse HTTP interface (port 8443, TLS) |',
        '| **User** | `agent` (readonly) |',
        '| **Databases** | `agent` (enriched tables), `curated` (analytics views) |',
        f'| **Max execution time** | {catalog["connection"]["settings"]["max_execution_time"]} |',
        f'| **Max memory** | {catalog["connection"]["settings"]["max_memory_usage"]} |',
        f'| **Max result rows** | {catalog["connection"]["settings"]["max_result_rows"]} |',
        '',
        '## Quick Start',
        '',
        '```sql',
        '-- Top DEX protocols by volume yesterday',
        'SELECT project, sum(amount_usd) AS volume_usd',
        'FROM agent.ethereum_dex_trades',
        'WHERE block_date = today() - 1',
        'GROUP BY project',
        'ORDER BY volume_usd DESC',
        'LIMIT 10',
        '```',
        '',
        '<Tip>',
        'Always filter on `block_date` first — it is the partition key for most tables and enables ClickHouse to skip entire partitions.',
        '</Tip>',
        '',
        '## Categories',
        '',
        '| Category | Tables | Description |',
        '|----------|--------|-------------|',
    ]

    # Build category table from catalog categories
    by_cat = defaultdict(list)
    for t in catalog["tables"]:
        by_cat[t["category"]].append(t)

    for cat_info in cats:
        name = cat_info["name"]
        slug = slugify(name)
        count = len(by_cat.get(name, []))
        desc = CATEGORY_DESCRIPTIONS.get(name, "")
        lines.append(f'| [{name}](/data-catalog/{slug}) | {count} | {desc} |')

    lines += [
        '',
        '## Query Best Practices',
        '',
    ]
    for i, practice in enumerate(practices, 1):
        lines.append(f'{i}. {practice}')

    lines += [
        '',
        '## Entity Linking',
        '',
        'Common join patterns across tables:',
        '',
    ]
    for link in entity_links:
        lines.append(f'- `{link}`')

    # Data freshness (list of pipeline entries)
    if freshness and isinstance(freshness, list):
        lines += [
            '',
            '## Data Freshness',
            '',
            '| Pipeline | Schedule | Typical Lag |',
            '|----------|----------|-------------|',
        ]
        for entry in freshness:
            pipeline = entry.get("pipeline", "")
            schedule = entry.get("schedule", "")
            lag = entry.get("lag", "")
            lines.append(f'| {pipeline} | {schedule} | {lag} |')
        lines += [
            '',
            'Check freshness for any table:',
            '',
            '```sql',
            'SELECT max(block_date) FROM agent.<table_name>',
            '```',
        ]

    lines.append('')
    return '\n'.join(lines)


def generate_category_page(cat_name: str, cat_desc: str, tables: list) -> str:
    slug = slugify(cat_name)

    lines = [
        '---',
        f'title: "{cat_name}"',
        f'description: "{cat_desc}"',
        '---',
        '',
        f'**{len(tables)} tables** in this category.',
        '',
        '## Tables',
        '',
        '| View Name | Database | Source | ORDER BY |',
        '|-----------|----------|--------|----------|',
    ]

    for t in tables:
        name = t.get("table_name", "")
        db = t.get("database", "")
        src = t.get("source", "")
        order = t.get("ordering_key", "—")
        if not order:
            order = "—"
        lines.append(f'| `{name}` | `{db}` | `{src}` | `{order}` |')

    # Related tables (collect from all tables in category)
    related = set()
    for t in tables:
        for rel in t.get("related_tables", []):
            rel_name = rel if isinstance(rel, str) else rel.get("table", "")
            if rel_name and rel_name not in [tt["table_name"] for tt in tables]:
                related.add(rel_name)

    if related:
        lines += ['', '## Related Tables', '']
        for rel in sorted(related):
            lines.append(f'- `{rel}`')

    # Sample queries (collect from all tables, deduplicate)
    sample_queries = []
    seen_titles = set()
    for t in tables:
        for sq in t.get("sample_queries", []):
            title = sq.get("title", sq.get("description", ""))
            if title not in seen_titles:
                seen_titles.add(title)
                sample_queries.append(sq)

    if sample_queries:
        lines += ['', '## Sample Queries', '']
        for i, sq in enumerate(sample_queries[:5], 1):  # cap at 5
            title = sq.get("title", sq.get("description", f"Query {i}"))
            sql = sq.get("sql", sq.get("query", ""))
            lines += [
                f'### {i}. {title}',
                '',
                '```sql',
                sql.strip(),
                '```',
                '',
            ]

    # Table schemas
    lines += ['## Table Schemas', '']
    for t in tables:
        name = t.get("table_name", "")
        engine = t.get("engine", "")
        partition = t.get("partition_key", "")
        order = t.get("ordering_key", "")
        desc = t.get("description", "")

        meta_parts = []
        if engine:
            meta_parts.append(f"**Engine**: {engine}")
        if partition:
            meta_parts.append(f"**Partition**: `{partition}`")
        if order:
            meta_parts.append(f"**ORDER BY**: `{order}`")
        meta_line = " | ".join(meta_parts)

        lines += [
            f'### `{name}`',
            '',
        ]
        if desc:
            lines += [desc, '']
        if meta_line:
            lines += [meta_line, '']

        columns = t.get("columns", [])
        if columns:
            lines += [
                '| Column | Type | Description |',
                '|--------|------|-------------|',
            ]
            for col in columns:
                col_name = col.get("name", "")
                col_type = col.get("type", "")
                col_desc = col.get("description", "")
                lines.append(f'| `{col_name}` | `{col_type}` | {col_desc} |')
            lines.append('')

        # Query tips
        tips = t.get("query_tips", [])
        if tips:
            lines += ['<Tip>', '']
            for tip in tips:
                lines.append(f'- {tip}')
            lines += ['', '</Tip>', '']

        # Limitations
        limitations = t.get("limitations", [])
        if limitations:
            lines += ['<Warning>', '']
            for lim in limitations:
                lines.append(f'- {lim}')
            lines += ['', '</Warning>', '']

    return '\n'.join(lines)


def main():
    with open(CATALOG_PATH) as f:
        catalog = json.load(f)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Group tables by category
    by_cat = defaultdict(list)
    for t in catalog["tables"]:
        by_cat[t["category"]].append(t)

    # Build category name -> description map
    cat_desc_map = {}
    for cat in catalog["categories"]:
        cat_desc_map[cat["name"]] = CATEGORY_DESCRIPTIONS.get(cat["name"], "")

    # Generate overview
    overview = generate_overview(catalog)
    (OUTPUT_DIR / "overview.mdx").write_text(overview)
    print(f"Generated: data-catalog/overview.mdx")

    # Generate category pages
    pages = []
    for cat in catalog["categories"]:
        name = cat["name"]
        slug = slugify(name)
        desc = CATEGORY_DESCRIPTIONS.get(name, "")
        tables = by_cat.get(name, [])
        if not tables:
            continue
        content = generate_category_page(name, desc, tables)
        (OUTPUT_DIR / f"{slug}.mdx").write_text(content)
        print(f"Generated: data-catalog/{slug}.mdx ({len(tables)} tables)")
        pages.append({"slug": slug, "name": name})

    # Print docs.json snippet for copy-paste
    print("\n--- docs.json tab snippet ---")
    page_entries = [f'                            "data-catalog/{p["slug"]}"' for p in pages]
    print(f"""            {{
                "tab": "Data Catalog",
                "groups": [
                    {{
                        "group": "Data Catalog",
                        "pages": [
                            "data-catalog/overview",
{chr(10).join(page_entries)}
                        ]
                    }}
                ]
            }}""")


if __name__ == "__main__":
    main()

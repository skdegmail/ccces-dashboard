"""
check_db.py -- print every row stored in responses.db in an easy-to-read format.

Run locally with:
    python check_db.py

Expects responses.db to be in the same folder as this script (created by
app.py once at least one survey response has been submitted).
"""

import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "responses.db"


def main():
    if not DB_PATH.exists():
        print(f"No database found at {DB_PATH}. Submit at least one survey response first.")
        sys.exit(1)

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM responses ORDER BY id").fetchall()

    if not rows:
        print("The database exists but has no saved responses yet.")
        return

    print(f"Found {len(rows)} saved response(s) in {DB_PATH.name}\n")

    for row in rows:
        raw_responses = json.loads(row["raw_responses_json"])
        construct_scores = json.loads(row["construct_scores_json"])
        factor_scores = json.loads(row["factor_scores_json"])

        print("=" * 60)
        print(f"Response ID: {row['id']}")
        print(f"Submitted (UTC): {row['submitted_at_utc']}")

        print("\nRaw item answers:")
        for item_id in sorted(raw_responses, key=int):
            print(f"  Item {item_id}: {raw_responses[item_id]}")

        print("\nConstruct mean scores:")
        for construct_id, value in construct_scores.items():
            print(f"  {construct_id}: {value:.2f}")

        print("\nFactor mean scores:")
        for factor_id, value in factor_scores.items():
            print(f"  Factor {factor_id}: {value:.2f}")

        print(f"\nOverall total mean: {row['total_score']:.2f}")
        print("=" * 60)
        print()


if __name__ == "__main__":
    main()

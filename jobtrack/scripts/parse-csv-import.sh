#!/usr/bin/env bash
# Parse a CSV of applications into normalized JSON using the FIELD_MAP aliases.
# Usage: parse-csv-import.sh <input.csv>
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: parse-csv-import.sh <input.csv>" >&2
  exit 1
fi

INPUT="$1"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$INPUT" ]; then
  echo "File not found: $INPUT" >&2
  exit 1
fi

node "$DIR/csv-import.js" "$INPUT"

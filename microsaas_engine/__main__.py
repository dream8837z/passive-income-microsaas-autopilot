"""CLI entrypoint for `python3 -m microsaas_engine run`."""
from __future__ import annotations

import json
import sys

from .pipeline import run_pipeline


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        result = run_pipeline()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

"""Simple database connectivity check."""

import sys

from db_connection import get_db_engine


def main() -> int:
    engine = get_db_engine()
    if engine is None:
        print("Test failed: could not create a database engine.")
        return 1

    print("Test passed: database connection is active.")
    engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

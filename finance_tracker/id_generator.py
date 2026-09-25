"""
Generates unique, persistent transaction IDs.

The requirement is:
- every transaction has a unique ID
- the ID must stay the same after the app restarts
- deleting a transaction must NOT change other transactions' IDs
- IDs must never be reused, even after a delete

The tempting-but-wrong approach is `next_id = max(existing_ids) + 1`
computed on the fly. That breaks the "never reused" rule: if the
highest-numbered transaction gets deleted, the next new transaction
would recompute the same max+1 and collide with an ID that used to
exist.

The fix: keep a single small file that only stores "the last ID we
ever handed out". It only ever increases, regardless of what gets
deleted from the main data file.
"""

import os

DEFAULT_NEXT_ID_FILE = os.path.join("data", "next_id.txt")


def get_next_id(path: str = DEFAULT_NEXT_ID_FILE) -> int:
    """
    Return the next available transaction ID and persist the update
    immediately, so the counter survives an application restart.

    `path` defaults to the real data file, but can be overridden --
    this is what makes the function easy to unit test without touching
    the project's actual data folder (see tests/test_id_generator.py).
    """
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    if not os.path.exists(path):
        current = 0
    else:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            current = int(content) if content else 0

    next_id = current + 1

    with open(path, "w", encoding="utf-8") as f:
        f.write(str(next_id))

    return next_id
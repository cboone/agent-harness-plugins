"""Hold an isolated audit lock while a supervised call reaches its limit."""

import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[2])
import checked_core as core

# The expected journal failure must stay outside the caller's ownership audit.
for name in ("CHECKED_SUPERVISION_AUDIT", "CHECKED_SUPERVISION_SCOPE"):
    os.environ.pop(name, None)
root = Path(sys.argv[1])
ready, spawned = root / "lock-ready", root / "spawned"
source = ("import fcntl,sys,time\nfrom pathlib import Path\n"
          "with open(sys.argv[1], 'rb') as stream:\n"
          " fcntl.flock(stream, fcntl.LOCK_EX)\n"
          " Path(sys.argv[2]).touch()\n time.sleep(6)\n")
record = dict(limit=3, call_error=None, finalization_error=None, elapsed=None)
try:
    with core.root_supervision(root) as runtime:
        holder = subprocess.Popen([sys.executable, "-c", source, str(runtime.journal.path), str(ready)])
        (root / "holder-pid").write_text(str(holder.pid))
        try:
            readiness = core.deadline_after(15)
            while not ready.exists():
                core.remaining(readiness, "audit lock fixture readiness")
                time.sleep(0.01)
            started = time.monotonic()
            try:
                core.command([sys.executable, "-c", "from pathlib import Path; Path('spawned').touch()"],
                             root, record["limit"])
            except (OSError, ValueError) as error:
                record["call_error"] = core.failure_cause(error)
            finally:
                record["elapsed"] = time.monotonic() - started
        finally:
            record["holder_exit"] = holder.wait(timeout=15)
except ValueError as error:
    record["finalization_error"] = core.failure_cause(error)
record["spawned"] = spawned.exists()
print(json.dumps(record))

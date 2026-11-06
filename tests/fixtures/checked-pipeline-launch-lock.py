"""Delay a pipeline stage's command record across its execution deadline."""

import json
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[2])
import checked_core as core

root = Path(sys.argv[1])
request, response, journal_path = root / "request.json", root / "response.json", root / "stage-journal.jsonl"
ready = root / "lock-ready"
core.FactJournal(journal_path, create=True)
holder = None
original = core.FactJournal
hold = 8
source = ("import fcntl,sys,time\nfrom pathlib import Path\n"
          "with open(sys.argv[1], 'rb') as stream:\n"
          " fcntl.flock(stream, fcntl.LOCK_EX)\n"
          " Path(sys.argv[2]).touch()\n time.sleep(float(sys.argv[3]))\n")


class DelayedJournal(original):
    def append(self, kind, target="root", **data):
        global holder
        if kind == "command" and holder is None:
            holder = subprocess.Popen([sys.executable, "-c", source, str(self.path), str(ready), str(hold)])
            (root / "holder-pid").write_text(str(holder.pid))
            readiness = core.deadline_after(15)
            while not ready.exists():
                core.remaining(readiness, "pipeline journal fixture readiness")
                time.sleep(0.01)
        return super().append(kind, target, **data)


with core.root_supervision() as runtime:
    allocation = runtime.allocate(hold * 3, pipeline=True)
    core.write_json(request, dict(stages=[[sys.executable, "-c", "pass"]], journal=str(journal_path),
                                 target="fixture", deadline=allocation["worker_deadline"],
                                 cleanup_deadline=allocation["execution_deadline"]))
    core.FactJournal = DelayedJournal
    try:
        core.pipeline_worker(request, response)
    finally:
        core.FactJournal = original
        holder_exit = holder.wait(timeout=15) if holder is not None else None
    report = core.parse_json(response.read_bytes())
    print(json.dumps(dict(holder_exit=holder_exit, report=report)))

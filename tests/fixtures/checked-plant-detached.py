"""Start an owned new-session descendant retaining the step's stdout and stderr."""

import os
from pathlib import Path
import subprocess
import sys
import time


with Path(os.environ["CHECKED_PLANT_PARENT_PIDS"]).open("a") as output:
    output.write(str(os.getpid()) + "\n")
child = r'''
import os
from pathlib import Path
import signal
import sys
import time
pid = os.getpid()
record = Path(os.environ["CHECKED_PLANT_CHILD_PIDS"])
def stop(signum, frame):
    record.with_name(str(pid) + ".stopped").write_text("stopped")
    raise SystemExit(0)
signal.signal(signal.SIGTERM, stop)
with record.open("a") as output:
    output.write(str(pid) + "\n")
print("detached stdout", flush=True)
print("detached stderr", file=sys.stderr, flush=True)
time.sleep(60)
'''
subprocess.Popen([sys.executable, "-c", child], start_new_session=True)
print("parent stdout", flush=True)
print("parent stderr", file=sys.stderr, flush=True)
time.sleep(60)

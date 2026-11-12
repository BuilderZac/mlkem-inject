import glob
import os
import threading
from pathlib import Path

import gdb


TARGET_NAME = "demoUse"
TARGET_EXECUTABLE = Path(
    os.environ.get(
        "MLKEM_TARGET",
        "/home/cmdr/Documents/cryptoProject/mlkem-native/demoUse",
    )
)
POLL_INTERVAL_SECONDS = 0.1
BREAKPOINT = "*0x405456"

attached = False
poll_pending = False


def find_target_pid():
    for comm_path in glob.glob("/proc/[0-9]*/comm"):
        try:
            pid = int(comm_path.split("/")[2])

            if pid == os.getpid():
                continue

            with open(comm_path, encoding="utf-8") as file:
                process_name = file.read().strip()

            if process_name == TARGET_NAME:
                return pid

        except (FileNotFoundError, PermissionError, OSError, ValueError):
            continue

    return None


def schedule_poll():
    global poll_pending

    if poll_pending or attached:
        return

    poll_pending = True
    timer = threading.Timer(POLL_INTERVAL_SECONDS, post_poll)
    timer.daemon = True
    timer.start()


def post_poll():
    gdb.post_event(poll_for_target)


class InjectionBreakpoint(gdb.Breakpoint):
    def __init__(self):
        super().__init__(
            BREAKPOINT,
            type=gdb.BP_BREAKPOINT,
            internal=True,
        )

    def stop(self):
        try:
            gdb.execute(
                "set {unsigned char}($r15+$rax) = 0xFF",
                to_string=True,
            )
            print("Injection applied; continuing.", flush=True)
            return False
        except gdb.error as error:
            print(f"Injection failed: {error}", flush=True)
            return True


def run_injection(pid):
    print(f"{TARGET_NAME} attached to PID {pid}", flush=True)
    print("Installing non-halting injection breakpoint.", flush=True)

    InjectionBreakpoint()

    # The breakpoint's stop() method returns False, so execution resumes
    # automatically after every injection.
    gdb.execute("continue")


def poll_for_target():
    global attached
    global poll_pending

    poll_pending = False

    if attached:
        return

    pid = find_target_pid()

    if pid is None:
        schedule_poll()
        return

    try:
        print(f"Found {TARGET_NAME}, PID {pid}; attaching...", flush=True)

        gdb.execute(f"file {TARGET_EXECUTABLE}")
        gdb.execute(f"attach {pid}")

        attached = True
        print(f"Attached to {TARGET_NAME}, PID {pid}", flush=True)

        gdb.post_event(lambda: run_injection(pid))

    except gdb.error as error:
        print(f"Attach failed: {error}", flush=True)
        schedule_poll()


def on_gdb_exit(_event):
    global attached
    attached = False
    print(f"{TARGET_NAME} exited.", flush=True)


gdb.events.exited.connect(on_gdb_exit)

print(f"Waiting for {TARGET_NAME}...", flush=True)
schedule_poll()

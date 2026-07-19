import argparse
import os
import signal
import sys
import time

from .config import MONITOR_INTERVAL, PID_FILE
from .jules_recovery_manager import JulesRecoveryManager
from tools.api.jules_api_client import JulesAPIClient


def create_pid_file():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def remove_pid_file():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def is_running():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            try:
                pid = int(f.read().strip())
                os.kill(pid, 0)
                return True
            except (ValueError, ProcessLookupError):
                return False
    return False

def monitor_loop(once=False):
    client = JulesAPIClient()
    manager = JulesRecoveryManager(client)

    print(f"Jules Monitor started (interval={MONITOR_INTERVAL}s)")

    while True:
        try:
            print(f"[{time.ctime()}] Checking sessions...")
            for session in client.list_sessions(page_size=10, max_results=10):
                session_id = session["name"]
                report = manager.analyze_session_state(session_id)
                if report["action"] in ["retry", "approve", "AUDIT"]:
                    manager.trigger_recovery(session_id, report["action"])

            if once:
                break
            time.sleep(MONITOR_INTERVAL)
        except KeyboardInterrupt:
            print("Monitor stopping...")
            break
        except Exception as e:
            print(f"Error in monitor loop: {e}")
            time.sleep(10)

def main():
    parser = argparse.ArgumentParser(description="Jules Session Monitor")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--interval", type=int, default=MONITOR_INTERVAL, help="Monitoring interval")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--stop", action="store_true", help="Stop the running daemon")

    args = parser.parse_args()

    if args.stop:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"Sent SIGTERM to process {pid}")
            except ProcessLookupError:
                print(f"Process {pid} not found")
            remove_pid_file()
        else:
            print("No PID file found")
        return

    if is_running() and not args.once:
        print("Monitor is already running")
        sys.exit(1)

    if args.daemon:
        # First fork
        try:
            pid = os.fork()
        except OSError as e:
            sys.stderr.write(f"fork failed: {e}\n")
            sys.exit(1)
        
        if pid > 0:
            sys.exit(0)  # Parent exits
        
        # Become session leader
        try:
            os.setsid()
        except OSError:
            # Already a session leader - that's okay, continue
            pass
        
        # Second fork
        try:
            pid = os.fork()
        except OSError as e:
            sys.stderr.write(f"second fork failed: {e}\n")
            sys.exit(1)
        
        if pid > 0:
            sys.exit(0)  # Parent exits

        # We're now a proper daemon
        create_pid_file()
        signal.signal(signal.SIGTERM, lambda signum, frame: remove_pid_file() or sys.exit(0))

        # Redirect stdout/stderr to a log file 
        log_file = open("jules_monitor.log", "a")
        sys.stdout = log_file
        sys.stderr = log_file
        
        try:
            monitor_loop()
        finally:
            log_file.close()
    else:
        monitor_loop(once=args.once)

if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Utility to run ARCHON's FastAPI backend and Streamlit UI with auto-reload.

This script supervises both servers, automatically restarting them when:
- Source files change (using the ``watchfiles`` library)
- A process crashes unexpectedly

Usage:
    python scripts/dev_servers.py

For CLI options, run with ``-h``.
"""

from __future__ import annotations

import argparse
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Iterable, List, Sequence

from watchfiles import watch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WATCH_PATHS = [PROJECT_ROOT / "src"]


def _as_command_line(command: Sequence[str]) -> str:
    return " ".join(command)


class ServiceWatcher:
    """Launch and monitor a single long-running server process."""

    def __init__(self, name: str, command: Sequence[str], watch_paths: Iterable[Path]):
        self.name = name
        self.command = list(command)
        self.watch_paths = tuple(str(Path(path)) for path in watch_paths)
        self.process: subprocess.Popen | None = None
        self.stop_event = threading.Event()
        self.restart_lock = threading.Lock()
        self.watch_thread: threading.Thread | None = None
        self.monitor_thread: threading.Thread | None = None

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------
    def start(self) -> None:
        self._start_process()
        self.watch_thread = threading.Thread(target=self._watch_loop, name=f"{self.name}-watch", daemon=True)
        self.monitor_thread = threading.Thread(target=self._monitor_loop, name=f"{self.name}-monitor", daemon=True)
        self.watch_thread.start()
        self.monitor_thread.start()

    def restart(self) -> None:
        with self.restart_lock:
            self._stop_process()
            self._start_process()

    def shutdown(self) -> None:
        self.stop_event.set()
        if self.watch_thread and self.watch_thread.is_alive():
            self.watch_thread.join(timeout=2)
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        with self.restart_lock:
            self._stop_process()

    # ------------------------------------------------------------------
    # Internal operations
    # ------------------------------------------------------------------
    def _start_process(self) -> None:
        cmd = _as_command_line(self.command)
        print(f"[{self.name}] starting: {cmd}")
        self.process = subprocess.Popen(self.command, cwd=PROJECT_ROOT)

    def _stop_process(self) -> None:
        if not self.process or self.process.poll() is not None:
            return
        print(f"[{self.name}] stopping...")
        self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print(f"[{self.name}] kill (graceful shutdown timed out)")
            self.process.kill()
        finally:
            self.process = None

    def _watch_loop(self) -> None:
        if not self.watch_paths:
            return
        print(f"[{self.name}] watching paths: {', '.join(self.watch_paths)}")
        for changes in watch(*self.watch_paths, stop_event=self.stop_event):
            if self.stop_event.is_set():
                break
            if not changes:
                continue
            change_count = len(changes)
            print(f"[{self.name}] detected {change_count} change(s); restarting...")
            self.restart()

    def _monitor_loop(self) -> None:
        while not self.stop_event.is_set():
            if self.process and self.process.poll() is not None:
                code = self.process.returncode
                print(f"[{self.name}] exited with code {code}; restarting...")
                self.restart()
            time.sleep(2)


def build_fastapi_command(port: int) -> List[str]:
    return [
        sys.executable,
        "-m",
        "uvicorn",
        "src.ui.api_server:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(port),
    ]


def build_streamlit_command(port: int) -> List[str]:
    return [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(PROJECT_ROOT / "src/ui/enhanced_web_interface.py"),
        f"--server.port={port}",
        "--server.headless=true",
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ARCHON dev servers with auto-reload")
    parser.add_argument("--api-port", type=int, default=8000, help="Port for the FastAPI server (default: 8000)")
    parser.add_argument(
        "--ui-port",
        type=int,
        default=8507,
        help="Port for the Streamlit UI (default: 8507)",
    )
    parser.add_argument(
        "--watch",
        action="append",
        default=None,
        help="Additional paths to watch for restarts (can be used multiple times). Defaults to src/",
    )
    return parser.parse_args()


def resolve_watch_paths(extra_paths: Iterable[str] | None) -> List[Path]:
    paths: List[Path] = list(DEFAULT_WATCH_PATHS)
    if extra_paths:
        for entry in extra_paths:
            candidate = (PROJECT_ROOT / entry).resolve() if not Path(entry).is_absolute() else Path(entry)
            if candidate.exists():
                paths.append(candidate)
            else:
                print(f"[dev_servers] Warning: watch path '{entry}' does not exist and will be skipped")
    return paths


def main() -> None:
    args = parse_args()
    watch_paths = resolve_watch_paths(args.watch)

    fastapi = ServiceWatcher("FastAPI", build_fastapi_command(args.api_port), watch_paths)
    streamlit = ServiceWatcher("Streamlit", build_streamlit_command(args.ui_port), watch_paths)

    services = [fastapi, streamlit]
    for service in services:
        service.start()

    stop_event = threading.Event()

    def handle_signal(signum, frame):  # type: ignore[unused-argument]
        print(f"[dev_servers] Received signal {signum}; shutting down...")
        stop_event.set()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        while not stop_event.is_set():
            time.sleep(0.5)
    finally:
        for service in services:
            service.shutdown()
        print("[dev_servers] All services stopped.")


if __name__ == "__main__":
    main()

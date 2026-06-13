import os
import signal
import subprocess
import sys
import time
from typing import Optional


def _env_mode() -> str:
    return os.getenv("RAILWAY_MODE", "all").strip().lower()


def _gunicorn_cmd() -> list[str]:
    port = os.getenv("PORT", "5001")
    workers = os.getenv("WEB_CONCURRENCY", "1")
    timeout = os.getenv("GUNICORN_TIMEOUT", "120")
    return [
        sys.executable,
        "-m",
        "gunicorn",
        "app:app",
        "--bind",
        f"0.0.0.0:{port}",
        "--workers",
        workers,
        "--timeout",
        timeout,
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
    ]


def _bot_cmd() -> list[str]:
    return [sys.executable, "bot.py"]


def _start(cmd: list[str], name: str) -> subprocess.Popen:
    print(f"[railway] starting {name}: {' '.join(cmd)}", flush=True)
    return subprocess.Popen(cmd)


def _stop(proc: Optional[subprocess.Popen], name: str) -> None:
    if proc is None or proc.poll() is not None:
        return
    print(f"[railway] stopping {name}...", flush=True)
    proc.terminate()
    deadline = time.time() + 15
    while time.time() < deadline:
        if proc.poll() is not None:
            return
        time.sleep(0.25)
    if proc.poll() is None:
        proc.kill()


def main() -> int:
    mode = _env_mode()
    if mode not in {"all", "web", "dashboard", "bot", "worker"}:
        print(f"[railway] invalid RAILWAY_MODE={mode!r}. Use all, dashboard, or bot.", flush=True)
        return 2

    dashboard: Optional[subprocess.Popen] = None
    bot: Optional[subprocess.Popen] = None
    shutting_down = False
    next_bot_restart = 0.0

    if mode in {"all", "web", "dashboard"}:
        dashboard = _start(_gunicorn_cmd(), "dashboard")
    if mode in {"all", "bot", "worker"}:
        bot = _start(_bot_cmd(), "discord-bot")

    def handle_signal(signum, frame):
        nonlocal shutting_down
        shutting_down = True
        print(f"[railway] received signal {signum}; stopping processes...", flush=True)
        _stop(bot, "discord-bot")
        _stop(dashboard, "dashboard")

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    try:
        while not shutting_down:
            if dashboard is not None and dashboard.poll() is not None:
                code = dashboard.returncode
                print(f"[railway] dashboard exited with code {code}; service cannot pass healthcheck.", flush=True)
                _stop(bot, "discord-bot")
                return int(code or 1)

            if bot is not None and bot.poll() is not None:
                code = bot.returncode
                if mode in {"bot", "worker"}:
                    print(f"[railway] discord-bot exited with code {code}.", flush=True)
                    return int(code or 1)

                # In all mode, keep the web dashboard alive so /healthz passes.
                # Restart the bot after a short delay and expose the real error in deploy logs.
                now = time.time()
                if now >= next_bot_restart:
                    print(f"[railway] discord-bot exited with code {code}; restarting in all mode.", flush=True)
                    next_bot_restart = now + 10
                    time.sleep(10)
                    if not shutting_down:
                        bot = _start(_bot_cmd(), "discord-bot")

            time.sleep(1)
    finally:
        _stop(bot, "discord-bot")
        _stop(dashboard, "dashboard")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

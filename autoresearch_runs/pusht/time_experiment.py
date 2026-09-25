#!/usr/bin/env python3
"""Run one Push-T experiment and append its wall-clock record to a CSV."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TIMING_CSV = ROOT / "autoresearch_runs/pusht/experiment_timing.csv"
LOG_DIR = ROOT / "autoresearch_runs/pusht/experiment_logs"
FIELDS = [
    "experiment_id",
    "kind",
    "label",
    "hypothesis",
    "start_utc",
    "end_utc",
    "wall_clock_seconds",
    "exit_code",
    "artifact_dir",
    "log_path",
    "coverage",
    "task_success",
    "episode_elapsed_s",
    "result_status",
]


def _root_relative(value: str, name: str) -> tuple[Path, str]:
    path = Path(value)
    resolved = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    try:
        relative = resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"{name} must resolve beneath repository root {ROOT}") from exc
    return resolved, relative.as_posix()


def _result_fields(artifact_dir: Path) -> dict[str, str]:
    result_path = artifact_dir / "result.json"
    if not result_path.is_file():
        return {"coverage": "", "task_success": "", "episode_elapsed_s": "", "result_status": "missing"}
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
        verification = data.get("verification", {})
        metrics = verification.get("metrics", {})
        coverage = metrics.get("coverage", verification.get("score", ""))
        success = data.get("success", verification.get("success", ""))
        elapsed = data.get("elapsed_s", "")
        return {
            "coverage": "" if coverage == "" else str(coverage),
            "task_success": "" if success == "" else str(bool(success)).lower(),
            "episode_elapsed_s": "" if elapsed == "" else str(elapsed),
            "result_status": "parsed",
        }
    except (OSError, json.JSONDecodeError, AttributeError, TypeError) as exc:
        return {"coverage": "", "task_success": "", "episode_elapsed_s": "", "result_status": f"parse_error: {type(exc).__name__}"}


def _append_row(row: dict[str, str]) -> None:
    TIMING_CSV.parent.mkdir(parents=True, exist_ok=True)
    exists = TIMING_CSV.exists()
    with TIMING_CSV.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow(row)
        stream.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--kind", choices=("scratch", "official"), required=True)
    parser.add_argument("--label", required=True, help="Short non-secret description of this one run")
    parser.add_argument("--hypothesis", required=True, help="Falsifiable hypothesis being evaluated")
    parser.add_argument("--artifact-dir", required=True, help="Fresh, repository-relative run output directory")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --")
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.experiment_id):
        parser.error("experiment-id may contain only letters, digits, dot, underscore, and hyphen")
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("provide a command after --")
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if Path(top).resolve() != ROOT:
            parser.error(f"runner root {ROOT} does not match Git root {top}")
        artifact_dir, artifact_relative = _root_relative(args.artifact_dir, "artifact-dir")
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        parser.error(str(exc))

    if artifact_dir.exists():
        parser.error(f"artifact directory already exists; use a fresh path: {artifact_relative}")

    TIMING_CSV.parent.mkdir(parents=True, exist_ok=True)
    if TIMING_CSV.exists():
        with TIMING_CSV.open(newline="", encoding="utf-8-sig") as stream:
            if any(row.get("experiment_id") == args.experiment_id for row in csv.DictReader(stream)):
                parser.error(f"experiment-id already recorded: {args.experiment_id}")

    log_path = LOG_DIR / f"{args.experiment_id}.log"
    if log_path.exists():
        parser.error(f"experiment log already exists; use a fresh experiment-id: {log_path.relative_to(ROOT)}")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    start = datetime.now(UTC)
    monotonic_start = time.monotonic()
    process: subprocess.Popen[str] | None = None
    exit_code = 1
    error = ""
    try:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        assert process.stdout is not None
        with log_path.open("w", encoding="utf-8") as log:
            for line in process.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                log.write(line)
                log.flush()
            exit_code = process.wait()
    except KeyboardInterrupt:
        error = "interrupted"
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        exit_code = 130
    except OSError as exc:
        error = f"launch_error: {type(exc).__name__}: {exc}"
        exit_code = 127
        log_path.write_text(error + "\n", encoding="utf-8")
    finally:
        end = datetime.now(UTC)
        elapsed = time.monotonic() - monotonic_start
        metrics = _result_fields(artifact_dir)
        row = {
            "experiment_id": args.experiment_id,
            "kind": args.kind,
            "label": args.label,
            "hypothesis": args.hypothesis,
            "start_utc": start.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "end_utc": end.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "wall_clock_seconds": f"{elapsed:.3f}",
            "exit_code": str(exit_code),
            "artifact_dir": artifact_relative,
            "log_path": log_path.relative_to(ROOT).as_posix(),
            **metrics,
        }
        if error:
            row["result_status"] = error
        _append_row(row)
        print(f"Timing recorded: {TIMING_CSV.relative_to(ROOT)} ({elapsed:.3f} wall-clock seconds)", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

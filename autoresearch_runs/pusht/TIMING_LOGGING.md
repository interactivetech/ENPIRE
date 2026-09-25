# Push-T experiment timing

`time_experiment.py` records one row per command run in `experiment_timing.csv`. It measures wall time with a monotonic clock and records UTC timestamps separately for ordering. It also saves command output to a per-run log without recording the full command line, which avoids copying potential credential arguments into the CSV.

## Required layout

- Scratch scripts/data: `autoresearch_runs/pusht/scratch/`
- Scratch outputs: `autoresearch_runs/pusht/scratch_runs/<experiment-id>/`
- Official outputs: `outputs/autoresearch/pusht/iteration-N/`
- Shared timing CSV: `autoresearch_runs/pusht/experiment_timing.csv`
- Captured stdout/stderr: `autoresearch_runs/pusht/experiment_logs/<experiment-id>.log`

The artifact directory must be a fresh path under the Git root. The runner refuses an existing path and duplicate experiment IDs to protect prior results. It launches the command with the repository root as its working directory and reads `result.json` from the artifact directory after the process exits.

## Scratch example

```bash
python autoresearch_runs/pusht/time_experiment.py \
  --experiment-id scratch-001 \
  --kind scratch \
  --label "translation-speed-40" \
  --hypothesis "Reducing translation speed to 40 improves final coverage." \
  --artifact-dir autoresearch_runs/pusht/scratch_runs/scratch-001 \
  -- uv run python autoresearch_runs/pusht/scratch/translation_speed_40.py \
       --output-dir autoresearch_runs/pusht/scratch_runs/scratch-001
```

## Official example

```bash
python autoresearch_runs/pusht/time_experiment.py \
  --experiment-id official-001 \
  --kind official \
  --label "iteration-1" \
  --hypothesis "The candidate policy improves final coverage over baseline." \
  --artifact-dir outputs/autoresearch/pusht/iteration-1 \
  -- uv run enpire examples run 20_simulated_pusht \
       --output outputs/autoresearch/pusht/iteration-1
```

Run one configuration per wrapper invocation. Failed and interrupted commands are recorded too. For the timing CSV to include coverage and task success, each run must produce an ENPIRE-compatible `result.json` in its artifact directory; scratch harnesses should write the same basic fields (`verification.metrics.coverage`, `success`, and `elapsed_s`).

`wall_clock_seconds` measures the complete wrapped process wall time. `episode_elapsed_s` is the simulator's own episode duration. To calculate elapsed time across a research session, subtract the first row's `start_utc` from the last row's `end_utc`; this includes gaps between runs but does not include planning before the first timed experiment or final analysis afterward.

# Push-T timing and run folders v3

`time_experiment.py` measures one wrapped command with a monotonic clock and records UTC start/end timestamps, wall time, the hypothesis, result coverage/success, artifact path, and exit status in `experiment_timing.csv`. It writes console output to a per-run log without storing the full command line.

## Required use

For the v3 protocol, use the wrapper once for the baseline and once for each numbered candidate. Always use `--kind official`. Never run scratch or diagnostic simulations. One wrapper invocation is one complete seed-0, 300-step Push-T episode; do not batch configurations or repeat a candidate.

The experiment folder is created before the run so it can hold the hypothesis and policy snapshot. Pass its new `run/` child as both `--artifact-dir` and the ENPIRE `--output`. The child must not already exist because the wrapper refuses to overwrite prior artifacts.

Example for iteration 1:

```bash
python autoresearch_runs/pusht/time_experiment.py \
  --experiment-id pusht-iteration-01 \
  --kind official \
  --label "iteration-01" \
  --hypothesis "This falsifiable policy change improves final coverage." \
  --artifact-dir outputs/autoresearch/pusht/experiments/iteration-01/run \
  -- uv run enpire examples run 20_simulated_pusht \
       --output outputs/autoresearch/pusht/experiments/iteration-01/run
```

Use the same shape for `pusht-baseline` and `experiments/baseline/run` for the one baseline run. Use IDs `pusht-iteration-02` through `pusht-iteration-10` for candidate folders. If a complete baseline folder and matching timing row already exist for a resumed session, reuse them rather than overwriting or rerunning.

## Where records live

- Per-run hypothesis, policy snapshot/diff, decision, copied log, and episode artifacts: `outputs/autoresearch/pusht/experiments/<baseline-or-iteration-NN>/`
- ENPIRE artifacts (including `animation.gif`): that experiment folder's `run/` child
- Master timing table: `autoresearch_runs/pusht/experiment_timing.csv`
- Original wrapper log: `autoresearch_runs/pusht/experiment_logs/<experiment-id>.log`; copy it to the matching experiment folder as `run.log`

The `outputs/` and log/CSV files are ignored by Git. Keep them in this worktree for later analysis; do not force-add them. At completion, match every run folder to exactly one timing row. Cumulative wall time is the final `end_utc` minus the first `start_utc`, which includes gaps between runs but excludes work before the first timed run and after the last one.

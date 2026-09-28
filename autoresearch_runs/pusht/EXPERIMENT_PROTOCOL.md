# Push-T experiment protocol v3

This protocol applies to the OpenCode v3 Push-T session. It replaces the v2 distinction between a capped number of official iterations and an unlimited scratch budget.

## Budget and evaluation

- Run one seed-0, 300-step baseline, then at most ten numbered candidate iterations.
- Each candidate iteration is exactly one complete ENPIRE Push-T episode. A launched attempt consumes its slot, including an invalid or failed run.
- Do not run any other Push-T simulation: no scratch runs, short or partial episodes, diagnostic probes, parameter sweeps, or duplicate evaluations. Do not create scratch experiment scripts.
- Existing non-simulator unit checks are allowed only when they do not launch the Push-T simulator. The single wrapped ENPIRE episode is the task evaluation for that candidate.
- Use final T-block coverage as the score. Keep a candidate only when it strictly improves on the best completed coverage; otherwise restore the best policy. Stop after ten candidates or at success (coverage >= 0.95).

## Allowed policy change

Edit only policy/action-selection code in `enpire/env/examples/20_simulated_pusht/example.py`. Keep seed, 300-step budget, reset, observations, dynamics, reward, verification, success threshold, safety, and artifact format fixed. Do not use real hardware.

## Folder contract

All run-specific work and outputs go under the ignored `outputs/autoresearch/pusht/experiments/` tree:

```text
experiments/
├── baseline/
│   ├── hypothesis.md
│   ├── policy_used.py
│   ├── decision.md
│   ├── run.log
│   └── run/
│       ├── result.json
│       ├── events.jsonl
│       ├── final_frame.png
│       └── animation.gif
├── iteration-01/
│   ├── hypothesis.md
│   ├── policy_before.py
│   ├── policy_used.py
│   ├── policy.diff
│   ├── decision.md
│   ├── run.log
│   └── run/  # same four ENPIRE episode artifacts
└── iteration-02/ ... iteration-10/
```

Create the folder and write its falsifiable hypothesis before editing policy code or launching the run. Save the exact policy used for that run. Do not overwrite any prior folder. A failed attempt keeps its folder and timing row; do not rerun it. If an infrastructure failure prevents continuing safely, stop and report it.

The simulator's `--output` must point to that folder's `run/` child. This keeps each episode's GIF, final frame, event stream, and result together with the hypothesis, policy snapshot, diff, decision, and copied log. Do not put task GIFs or run-specific code in a shared scratch directory.

## Timing record

Launch every baseline and candidate through `autoresearch_runs/pusht/time_experiment.py` with `--kind official`, one unique ID, and the hypothesis for that folder. The wrapper writes one row to `autoresearch_runs/pusht/experiment_timing.csv` and a log to `autoresearch_runs/pusht/experiment_logs/<experiment-id>.log`; copy that log to the corresponding folder as `run.log` after completion. Never invoke it with `--kind scratch`.

At the end, verify there is exactly one row for the baseline and each launched candidate, with each row's artifact path pointing to that experiment's `run/` folder. Report per-run `wall_clock_seconds` and cumulative wall time as the last `end_utc` minus the first `start_utc`; do not substitute the simulator's `elapsed_s` or sum run durations for cumulative research time.

## Completion

Reconcile all experiment folders, timing rows, `result.json` files, and GIFs. Record each result, success value, artifact completeness, and keep/revert decision in that folder's `decision.md`. Report the baseline, attempted candidates, best coverage/success, cumulative timing, and final policy diff. Do not commit or push from OpenCode.

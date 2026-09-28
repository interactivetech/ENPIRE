# OpenCode prompt: Push-T autoresearch v3

Launch OpenCode from the root of the `opencode-vllm-test-v3` worktree, then paste this prompt:

```text
Read AGENTS.md, enpire/policy/autoresearch_instruction.md, enpire/env/examples/20_simulated_pusht/README.md, autoresearch_runs/pusht/EXPERIMENT_PROTOCOL.md, and autoresearch_runs/pusht/TIMING_LOGGING.md.

Before editing anything, run `pwd`, `git rev-parse --show-toplevel`, and `git branch --show-current`. Confirm that the current directory is the Git root and the branch is `opencode-vllm-test-v3`. If not, stop and report the paths. Do not switch checkouts.

Objective: improve final T-block coverage for the simulated Push-T task. Seed 0, 300 steps, coverage score, and the 0.95 success threshold are fixed. Edit only policy/action-selection code in `enpire/env/examples/20_simulated_pusht/example.py`. Do not change simulator dynamics, reset behavior, observations, reward, verification, safety, thresholds, step count, seed, or artifact format. Never use real hardware.

There is one baseline run plus at most TEN numbered candidate iterations. These are the entire simulator-run budget. One iteration means exactly one full 300-step ENPIRE episode, launched through `time_experiment.py`. Do not run scratch experiments, partial episodes, diagnostic probes, parameter sweeps, duplicate evaluations, or any other Push-T simulator command. Do not write or execute scratch policy scripts. Existing non-simulator unit checks may be run only if they do not launch Push-T; the single wrapped episode is the offline Push-T evaluation.

Keep all experiment material beneath this Git root. Use `outputs/autoresearch/pusht/experiments/baseline/` for the baseline and `outputs/autoresearch/pusht/experiments/iteration-01/` through `iteration-10/` for candidates. Do not use `/tmp`, system temp directories, `$HOME`, or another checkout. These output folders are Git-ignored; do not force-add or commit their contents.

For each run, create its folder before editing or launching. Write `hypothesis.md` before changing the policy. Save the exact policy used as `policy_used.py`; for candidates, also save `policy_before.py` and `policy.diff` against the current best. Put ENPIRE episode artifacts in that folder's `run/` child and the completed decision in `decision.md`. Use unique IDs `pusht-baseline` and `pusht-iteration-01` through `pusht-iteration-10`.

Run the baseline once through the timing wrapper if this session has no complete baseline folder and matching timing row. For each candidate, make one small policy-only change and run exactly once using this form (replace the ID, label, hypothesis, and folder for that numbered iteration):

`python autoresearch_runs/pusht/time_experiment.py --experiment-id pusht-iteration-01 --kind official --label "iteration-01" --hypothesis "Falsifiable statement about final coverage" --artifact-dir outputs/autoresearch/pusht/experiments/iteration-01/run -- uv run enpire examples run 20_simulated_pusht --output outputs/autoresearch/pusht/experiments/iteration-01/run`

The baseline uses the same command shape with ID `pusht-baseline`, folder `baseline`, and its own falsifiable control hypothesis. Do not overwrite an existing folder. The wrapper log is initially written to `autoresearch_runs/pusht/experiment_logs/<experiment-id>.log`; after the run, copy it into that experiment folder as `run.log`. Keep the aggregate timing row in `autoresearch_runs/pusht/experiment_timing.csv`.

Wait for each episode to finish. A completed run must have `run/result.json`, `run/events.jsonl`, `run/final_frame.png`, and `run/animation.gif`. If a run exits unsuccessfully or any expected artifact is missing, preserve its folder and timing record; do not rerun it. Stop and report if an infrastructure failure prevents valid continuation. Each launched candidate consumes its numbered slot, including failed attempts.

Compare final coverage with the best completed result. Keep a candidate only when coverage strictly improves; otherwise restore the best policy before the next candidate. Stop after ten candidate slots or once task success is true (coverage >= 0.95), whichever comes first. Never start iteration 11.

After each run, record its score, success, timing row, artifact checklist, and keep/revert decision in that experiment's `decision.md`. At completion, reconcile folders against the timing CSV and report the baseline, every attempted candidate, per-run wall-clock time, cumulative time from first start to last end, best coverage/success, and current policy diff. Do not generate shared scratch plots or GIFs. Do not commit or push.
```

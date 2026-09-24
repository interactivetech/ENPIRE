# Simulated Push-T

Run the standard planar Push-T physics task in Gymnasium through ENPIRE's
reset-execute-verify loop. This is independent of the real-YAM Push-T CaP
workflow.

The simulator uses a 2D physics engine: the observation is the pusher and T
block state, and each action sets the pusher's target point. Reward measures
how much of the T block overlaps the goal; success is at least 95% coverage.
The runnable policy is a seeded random-action baseline, not a trained solver.

Install the optional simulator dependency and run an episode:

```bash
uv sync --extra dev --extra sim-pusht
uv run enpire examples run 20_simulated_pusht
```

The example uses a seeded random-action baseline, so success is not expected
on every run. `result.json` records the final coverage reward and success
status; `events.jsonl` records each transition. In the default `rgb_array`
mode, `animation.gif` contains the initial state and one frame per action, and
`final_frame.png` shows the last state. The terminal prints startup/reset
messages and progress every 25 actions.

After the run, open the animation on a desktop with:

```bash
xdg-open outputs/simulated-pusht/animation.gif
```

To open the live simulation window on a machine with a display:

```bash
ENPIRE_PUSHT_RENDER_MODE=human uv run enpire examples run 20_simulated_pusht
```

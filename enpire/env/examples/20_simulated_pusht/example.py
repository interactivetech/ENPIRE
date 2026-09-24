# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Run Gymnasium's Push-T physics environment through ENPIRE's trial loop."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from enpire.env.forge.artifacts import ArtifactStore
from enpire.env.forge.interface import StepResult, VerificationResult
from enpire.env.forge.loop import TrialRunner
from enpire.policy.interface import FunctionPolicy


class PushTSimulation:
    """Adapt the optional Gymnasium Push-T package to ENPIRE's environment API."""

    def __init__(self) -> None:
        print("[Push-T] initializing simulator", flush=True)
        try:
            import gymnasium as gym
            import gym_pusht  # noqa: F401  # Registers gym_pusht/PushT-v0.
        except ImportError as exc:
            raise RuntimeError(
                "Push-T simulation dependencies are missing; install with "
                "`uv sync --extra dev --extra sim-pusht`."
            ) from exc

        render_mode = os.environ.get("ENPIRE_PUSHT_RENDER_MODE", "rgb_array")
        if render_mode not in {"rgb_array", "human"}:
            raise ValueError("ENPIRE_PUSHT_RENDER_MODE must be 'rgb_array' or 'human'")
        self.render_mode = render_mode
        self._gym_env = gym.make(
            "gym_pusht/PushT-v0",
            obs_type="state",
            render_mode=render_mode,
        )
        self._last_reward = 0.0
        self._terminated = False
        self._observation: Any = None
        self._frames: list[Any] = []
        print(f"[Push-T] simulator ready (render_mode={render_mode})", flush=True)

    def reset(self, *, seed: int | None = None) -> Any:
        print(f"[Push-T] resetting environment (seed={seed})", flush=True)
        observation, _info = self._gym_env.reset(seed=seed)
        if seed is not None:
            self._gym_env.action_space.seed(seed)
        self._last_reward = 0.0
        self._terminated = False
        self._observation = observation
        if self.render_mode == "human":
            self._gym_env.render()
        else:
            self._frames.clear()
            self._capture_frame()
        print("[Push-T] environment reset complete", flush=True)
        return observation

    def observe(self) -> Any:
        return self._observation

    def sample_action(self) -> Any:
        return self._gym_env.action_space.sample()

    @property
    def coverage(self) -> float:
        return self._last_reward

    def step(self, action: Any) -> StepResult:
        observation, reward, terminated, truncated, info = self._gym_env.step(action)
        self._last_reward = float(reward)
        self._terminated = bool(terminated)
        self._observation = observation
        if self.render_mode == "human":
            self._gym_env.render()
        else:
            self._capture_frame()
        return StepResult(
            observation=observation,
            reward=self._last_reward,
            terminated=bool(terminated),
            truncated=bool(truncated),
            info=info,
        )

    def verify(self) -> VerificationResult:
        return VerificationResult(
            success=self._terminated,
            score=self._last_reward,
            reason=None if self._terminated else "Push-T goal coverage stayed below 95%.",
            metrics={"coverage": self._last_reward, "success_threshold": 0.95},
        )

    def save_frame(self, path: Path) -> bool:
        if self.render_mode != "rgb_array":
            return False
        if not self._frames:
            return False
        self._frames[-1].save(path)
        return True

    def save_animation(self, path: Path) -> bool:
        if self.render_mode != "rgb_array" or not self._frames:
            return False
        self._frames[0].save(
            path,
            save_all=True,
            append_images=self._frames[1:],
            duration=100,
            loop=0,
            disposal=2,
            optimize=True,
        )
        return True

    def _capture_frame(self) -> None:
        frame = self._gym_env.render()
        if frame is None:
            return
        from PIL import Image

        image = Image.fromarray(frame).convert("RGB")
        image.thumbnail((320, 320))
        self._frames.append(image.copy())

    def close(self) -> None:
        self._gym_env.close()


def main(*, output: str | Path = "outputs/simulated-pusht") -> int:
    output_path = Path(output)
    environment = PushTSimulation()
    max_steps = 300
    step_count = 0

    def choose_action(_observation: Any) -> Any:
        nonlocal step_count
        step_count += 1
        if step_count == 1 or step_count % 25 == 0:
            print(
                f"[Push-T] step {step_count}/{max_steps} "
                f"coverage={environment.coverage:.3f}",
                flush=True,
            )
        return environment.sample_action()

    policy = FunctionPolicy(choose_action)
    runner = TrialRunner(
        environment,
        policy,
        artifacts=ArtifactStore(output_path),
        max_steps=max_steps,
    )
    print(f"[Push-T] starting episode (seed=0, max_steps={max_steps})", flush=True)
    animation_saved = False
    try:
        result = runner.run(seed=0)
        environment.save_frame(output_path / "final_frame.png")
        animation_saved = environment.save_animation(output_path / "animation.gif")
    finally:
        runner.close()
    animation_summary = (
        f" animation={output_path / 'animation.gif'}" if animation_saved else ""
    )
    print(
        f"[Push-T] finished: success={result.success} steps={result.steps} "
        f"coverage={result.verification.score:.3f} output={output_path}"
        f"{animation_summary}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

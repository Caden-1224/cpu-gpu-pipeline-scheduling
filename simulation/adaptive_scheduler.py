"""Adaptive CPU task-selection policy for a CPU-GPU pipeline prototype.

This module implements only task scoring and selection. It is not a Linux
``sched_ext`` or eBPF program and must not be used as evidence of deployment.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TaskType(str, Enum):
    """Stages that can compete for a CPU core.

    Written as ``(str, Enum)`` rather than ``enum.StrEnum`` so the package runs on
    Python 3.10 as well; the members are used comparatively, never formatted.
    """

    PREPROCESS = "preprocess"
    SUBMIT = "submit"
    POSTPROCESS = "postprocess"
    BACKGROUND = "background"


@dataclass(frozen=True)
class ReadyTask:
    """A CPU task eligible for dispatch."""

    task_type: TaskType
    ready_time_ms: float
    ready_order: int


@dataclass(frozen=True)
class SchedulerWeights:
    """Fixed weights for one experiment configuration."""

    gpu: float
    wait: float
    stage: float
    age: float


@dataclass(frozen=True)
class SchedulerLimits:
    """Safety and normalization bounds for the scheduler."""

    min_target_pending: int
    max_target_pending: int
    starvation_limit_ms: float


def clamp(value: int, lower: int, upper: int) -> int:
    """Constrain an integer to an inclusive range."""
    return max(lower, min(value, upper))


def update_target_pending(
    gpu_service_ema_ms: float | None,
    reference_gpu_ms: float,
    previous_target: int,
    limits: SchedulerLimits,
) -> int:
    """Adapt the target GPU in-flight count from measured GPU service time."""
    if limits.min_target_pending < 1:
        raise ValueError("min_target_pending must be at least one")
    if limits.max_target_pending < limits.min_target_pending:
        raise ValueError("max_target_pending must not be smaller than minimum")
    if reference_gpu_ms <= 0:
        raise ValueError("reference_gpu_ms must be positive")
    if gpu_service_ema_ms is None or gpu_service_ema_ms <= 0:
        return clamp(previous_target, limits.min_target_pending, limits.max_target_pending)

    proposed_target = round(reference_gpu_ms / gpu_service_ema_ms)
    return clamp(proposed_target, limits.min_target_pending, limits.max_target_pending)


def update_ema(previous: float | None, observation: float, alpha: float) -> float:
    """Update an exponential moving average with a positive observation."""
    if not 0 < alpha <= 1:
        raise ValueError("alpha must be in (0, 1]")
    if observation <= 0:
        raise ValueError("observation must be positive")
    return observation if previous is None else alpha * observation + (1 - alpha) * previous


def _normalize(value: float, scale: float) -> float:
    if scale <= 0:
        return 0.0
    return min(1.0, max(0.0, value / scale))


def compute_score(
    task: ReadyTask,
    gpu_pending: int,
    target_gpu_pending: int,
    now_ms: float,
    weights: SchedulerWeights,
    limits: SchedulerLimits,
) -> float:
    """Score a task using GPU pressure, waiting time, stage, and aging."""
    if gpu_pending < 0:
        raise ValueError("gpu_pending must not be negative")
    if target_gpu_pending < 1:
        raise ValueError("target_gpu_pending must be at least one")

    waiting_ms = max(0.0, now_ms - task.ready_time_ms)
    wait_score = _normalize(waiting_ms, limits.starvation_limit_ms)
    if task.task_type is TaskType.SUBMIT:
        gpu_urgency = _normalize(target_gpu_pending - gpu_pending, target_gpu_pending)
        stage_score = 1.0
    elif task.task_type is TaskType.PREPROCESS:
        gpu_urgency = _normalize(gpu_pending - target_gpu_pending, target_gpu_pending)
        stage_score = 0.8
    elif task.task_type is TaskType.POSTPROCESS:
        gpu_urgency = 0.0
        stage_score = 0.6
    else:
        gpu_urgency = 0.0
        stage_score = 0.2

    age_bonus = float(waiting_ms >= limits.starvation_limit_ms)
    return (
        weights.gpu * gpu_urgency
        + weights.wait * wait_score
        + weights.stage * stage_score
        + weights.age * age_bonus
    )


def select_adaptive_task(
    ready_tasks: list[ReadyTask],
    gpu_pending: int,
    target_gpu_pending: int,
    now_ms: float,
    weights: SchedulerWeights,
    limits: SchedulerLimits,
) -> ReadyTask:
    """Return the maximum-score task, preserving ready order for ties."""
    if not ready_tasks:
        raise ValueError("ready_tasks must not be empty")
    return max(
        ready_tasks,
        key=lambda task: (
            compute_score(task, gpu_pending, target_gpu_pending, now_ms, weights, limits),
            -task.ready_order,
        ),
    )

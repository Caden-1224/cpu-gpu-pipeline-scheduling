import unittest

from simulation.adaptive_scheduler import (
    ReadyTask,
    SchedulerLimits,
    SchedulerWeights,
    TaskType,
    select_adaptive_task,
    update_target_pending,
)


class AdaptiveSchedulerTests(unittest.TestCase):
    def setUp(self):
        self.limits = SchedulerLimits(1, 4, 10.0)
        self.weights = SchedulerWeights(gpu=2.0, wait=0.4, stage=0.2, age=3.0)

    def test_underfilled_gpu_prefers_submit(self):
        tasks = [
            ReadyTask(TaskType.PREPROCESS, 0.0, 0),
            ReadyTask(TaskType.SUBMIT, 0.0, 1),
        ]
        selected = select_adaptive_task(tasks, 0, 1, 1.0, self.weights, self.limits)
        self.assertEqual(selected.task_type, TaskType.SUBMIT)

    def test_aged_background_task_is_not_starved(self):
        tasks = [
            ReadyTask(TaskType.BACKGROUND, 0.0, 0),
            ReadyTask(TaskType.SUBMIT, 9.0, 1),
        ]
        selected = select_adaptive_task(tasks, 0, 1, 10.0, self.weights, self.limits)
        self.assertEqual(selected.task_type, TaskType.BACKGROUND)

    def test_target_is_limited_and_preserved_without_measurement(self):
        self.assertEqual(update_target_pending(None, 1.0, 9, self.limits), 4)
        self.assertEqual(update_target_pending(0.1, 1.0, 1, self.limits), 4)


if __name__ == "__main__":
    unittest.main()

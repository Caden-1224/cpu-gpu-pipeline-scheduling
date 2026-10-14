import unittest

from simulation.run_experiment import POLICIES, PROFILES, simulate


class ExperimentTests(unittest.TestCase):
    def test_every_request_completes(self):
        rows, summary = simulate("steady", "fifo", 1000)
        self.assertEqual(len(rows), PROFILES["steady"].request_count)
        self.assertEqual(summary["requests"], len(rows))
        self.assertTrue(all(float(row["latency_ms"]) > 0 for row in rows))

    def test_repeatable_for_a_seed(self):
        _, first = simulate("cpu_contention", "gpu_feedback", 2000)
        _, second = simulate("cpu_contention", "gpu_feedback", 2000)
        self.assertEqual(first, second)

    def test_all_policies_produce_metrics(self):
        for policy in POLICIES:
            _, summary = simulate("bursty", policy, 3000)
            self.assertGreater(float(summary["throughput_req_per_ms"]), 0)
            self.assertGreaterEqual(float(summary["gpu_busy_ratio"]), 0)
            self.assertLessEqual(float(summary["gpu_busy_ratio"]), 1)

    def test_default_feedback_threshold_is_one(self):
        _, default = simulate("cpu_contention", "gpu_feedback", 2000)
        _, explicit = simulate(
            "cpu_contention", "gpu_feedback", 2000, gpu_pending_threshold=1
        )
        self.assertEqual(default, explicit)

    def test_feedback_threshold_is_configurable(self):
        _, low = simulate(
            "cpu_contention", "gpu_feedback", 2000, gpu_pending_threshold=0
        )
        _, high = simulate(
            "cpu_contention", "gpu_feedback", 2000, gpu_pending_threshold=4
        )
        self.assertNotEqual(low["p99_latency_ms"], high["p99_latency_ms"])

    def test_negative_feedback_threshold_is_rejected(self):
        with self.assertRaises(ValueError):
            simulate("steady", "gpu_feedback", 1000, gpu_pending_threshold=-1)


if __name__ == "__main__":
    unittest.main()

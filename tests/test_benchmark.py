"""Tests for incept.training.benchmark — multi-adapter merge + benchmark report."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from incept.training.benchmark import (
    BenchmarkReport,
    merge_multiple_adapters,
    run_benchmark,
)

# ========================== merge_multiple_adapters ==========================


class TestMergeMultipleAdapters:
    @patch("incept.training.benchmark.merge_lora_adapter")
    def test_merges_each_adapter_sequentially(self, mock_merge: MagicMock, tmp_path: Path) -> None:
        base = tmp_path / "base"
        adapter1 = tmp_path / "adapter1"
        adapter2 = tmp_path / "adapter2"
        output = tmp_path / "output"

        mock_merge.return_value = output

        result = merge_multiple_adapters(
            base_path=base,
            adapter_paths=[adapter1, adapter2],
            output_path=output,
        )

        assert mock_merge.call_count == 2
        # First call: base + adapter1 → intermediate
        first_call = mock_merge.call_args_list[0]
        assert first_call[1]["base_path"] == base
        assert first_call[1]["adapter_path"] == adapter1
        # Second call: intermediate + adapter2 → output
        second_call = mock_merge.call_args_list[1]
        assert second_call[1]["adapter_path"] == adapter2
        assert result == output

    @patch("incept.training.benchmark.merge_lora_adapter")
    def test_single_adapter(self, mock_merge: MagicMock, tmp_path: Path) -> None:
        base = tmp_path / "base"
        adapter = tmp_path / "adapter"
        output = tmp_path / "output"

        mock_merge.return_value = output

        result = merge_multiple_adapters(
            base_path=base,
            adapter_paths=[adapter],
            output_path=output,
        )

        mock_merge.assert_called_once()
        assert result == output

    @patch("incept.training.benchmark.merge_lora_adapter")
    def test_empty_adapter_list_returns_base(self, mock_merge: MagicMock, tmp_path: Path) -> None:
        base = tmp_path / "base"
        output = tmp_path / "output"

        result = merge_multiple_adapters(
            base_path=base,
            adapter_paths=[],
            output_path=output,
        )

        mock_merge.assert_not_called()
        assert result == base


# ========================== BenchmarkReport ==========================


class TestBenchmarkReport:
    def test_valid_report(self) -> None:
        report = BenchmarkReport(
            model_name="incept-q4_k_m",
            safety_pass_rate=1.0,
            grammar_validity=0.98,
        )
        assert report.model_name == "incept-q4_k_m"
        assert report.intent_metrics is None
        assert report.slot_metrics is None
        assert report.safety_pass_rate == 1.0
        assert report.grammar_validity == 0.98
        assert report.timestamp

    def test_with_metrics(self) -> None:
        from incept.eval.metrics import IntentMetrics, SlotMetrics

        intent_m = IntentMetrics(accuracy=0.93, total=100, correct=93)
        slot_m = SlotMetrics(exact_match=0.85, slot_f1=0.88, total=100)

        report = BenchmarkReport(
            model_name="incept-merged",
            intent_metrics=intent_m,
            slot_metrics=slot_m,
            safety_pass_rate=1.0,
            grammar_validity=0.99,
        )
        assert report.intent_metrics.accuracy == 0.93
        assert report.slot_metrics.slot_f1 == 0.88

    def test_serializes_to_json(self) -> None:
        report = BenchmarkReport(
            model_name="test",
            safety_pass_rate=0.99,
            grammar_validity=0.95,
        )
        data = json.loads(report.model_dump_json())
        assert data["model_name"] == "test"
        assert data["safety_pass_rate"] == 0.99
        assert "timestamp" in data


# ========================== run_benchmark ==========================


class TestRunBenchmark:
    @patch("incept.training.benchmark.validate_canary_pass_rate", return_value=1.0)
    @patch("incept.training.benchmark.generate_canaries")
    @patch("incept.training.benchmark.compute_slot_metrics")
    @patch("incept.training.benchmark.compute_intent_accuracy")
    def test_returns_benchmark_report(
        self,
        mock_intent_acc: MagicMock,
        mock_slot_metrics: MagicMock,
        mock_gen_canaries: MagicMock,
        mock_validate: MagicMock,
        tmp_path: Path,
    ) -> None:
        from incept.eval.metrics import IntentMetrics, SlotMetrics

        mock_intent_acc.return_value = IntentMetrics(accuracy=0.93, total=100, correct=93)
        mock_slot_metrics.return_value = SlotMetrics(exact_match=0.85, slot_f1=0.88, total=100)
        mock_gen_canaries.return_value = []

        # Create test data dir with non-empty data so the guard passes
        intent_dir = tmp_path / "intent"
        intent_dir.mkdir()
        (intent_dir / "predictions.json").write_text('["find_files"]')
        (intent_dir / "ground_truth.json").write_text('["find_files"]')
        slot_dir = tmp_path / "slot"
        slot_dir.mkdir()
        (slot_dir / "predictions.json").write_text('[{"path": "/tmp"}]')
        (slot_dir / "ground_truth.json").write_text('[{"path": "/tmp"}]')
        (slot_dir / "intents.json").write_text('["find_files"]')

        report = run_benchmark(
            model_path=str(tmp_path / "model.gguf"),
            test_data_dir=str(tmp_path),
        )

        assert isinstance(report, BenchmarkReport)
        assert report.intent_metrics is not None
        assert report.intent_metrics.accuracy == 0.93
        assert report.slot_metrics is not None
        assert report.slot_metrics.slot_f1 == 0.88
        assert report.safety_pass_rate == 1.0

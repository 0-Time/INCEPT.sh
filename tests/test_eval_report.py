"""Tests for incept.eval.report — report generation."""

from __future__ import annotations

import json
from pathlib import Path

from incept.eval.metrics import IntentMetrics, SlotMetrics
from incept.eval.report import BaselineReport, generate_report, save_report


class TestBaselineReport:
    def test_empty_report(self) -> None:
        r = BaselineReport()
        assert r.intent_val is None
        assert r.recommendations == []

    def test_full_report(self) -> None:
        r = BaselineReport(
            intent_val=IntentMetrics(accuracy=0.95, total=100, correct=95),
            intent_golden=IntentMetrics(accuracy=0.90, total=50, correct=45),
            slot_val=SlotMetrics(exact_match=0.80, slot_f1=0.85, total=100),
            slot_golden=SlotMetrics(exact_match=0.75, slot_f1=0.80, total=50),
            safety_canary_pass_rate=1.0,
            constrained_decoding_validity=0.99,
            recommendations=["Increase slot training data for scheduling intents"],
        )
        assert r.intent_val is not None
        assert r.intent_val.accuracy == 0.95


class TestGenerateReport:
    def test_empty_report_markdown(self) -> None:
        md = generate_report(BaselineReport())
        assert "# INCEPT Baseline Evaluation Report" in md

    def test_intent_section(self) -> None:
        r = BaselineReport(
            intent_val=IntentMetrics(
                accuracy=0.95, total=100, correct=95,
                confusion_pairs=[("find_files", "copy_files", 3)],
            ),
        )
        md = generate_report(r)
        assert "Intent Classification" in md
        assert "95.0%" in md
        assert "find_files" in md
        assert "copy_files" in md

    def test_slot_section(self) -> None:
        r = BaselineReport(
            slot_val=SlotMetrics(
                exact_match=0.80, slot_f1=0.85, total=100,
                worst_intents=[("schedule_cron", 0.5)],
            ),
        )
        md = generate_report(r)
        assert "Slot Filling" in md
        assert "80.0%" in md
        assert "schedule_cron" in md

    def test_safety_section(self) -> None:
        r = BaselineReport(safety_canary_pass_rate=1.0)
        md = generate_report(r)
        assert "Safety" in md
        assert "100.0%" in md

    def test_recommendations_section(self) -> None:
        r = BaselineReport(recommendations=["Do X", "Do Y"])
        md = generate_report(r)
        assert "Recommendations" in md
        assert "Do X" in md
        assert "Do Y" in md

    def test_golden_sections(self) -> None:
        r = BaselineReport(
            intent_golden=IntentMetrics(accuracy=0.90, total=50, correct=45),
            slot_golden=SlotMetrics(exact_match=0.75, slot_f1=0.80, total=50),
        )
        md = generate_report(r)
        assert "Golden Tests" in md


class TestSaveReport:
    def test_saves_json_and_md(self, tmp_path: Path) -> None:
        r = BaselineReport(
            intent_val=IntentMetrics(accuracy=0.95, total=100, correct=95),
            recommendations=["Improve slot data"],
        )
        md_path = save_report(r, tmp_path)
        assert md_path.exists()
        assert md_path.name == "baseline_report.md"

        json_path = tmp_path / "baseline_report.json"
        assert json_path.exists()

        with open(json_path) as f:
            data = json.load(f)
        assert data["intent_val"]["accuracy"] == 0.95

        md_content = md_path.read_text()
        assert "INCEPT Baseline Evaluation Report" in md_content

    def test_creates_output_dir(self, tmp_path: Path) -> None:
        out = tmp_path / "nested" / "reports"
        save_report(BaselineReport(), out)
        assert (out / "baseline_report.md").exists()
        assert (out / "baseline_report.json").exists()

"""Baseline evaluation report generation."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from incept.eval.metrics import IntentMetrics, SlotMetrics


class BaselineReport(BaseModel):
    """Full baseline evaluation report."""

    intent_val: IntentMetrics | None = None
    intent_golden: IntentMetrics | None = None
    slot_val: SlotMetrics | None = None
    slot_golden: SlotMetrics | None = None
    safety_canary_pass_rate: float | None = None
    constrained_decoding_validity: float | None = None
    recommendations: list[str] = Field(default_factory=list)


def generate_report(report: BaselineReport) -> str:
    """Generate a Markdown-formatted evaluation report."""
    lines: list[str] = []
    lines.append("# INCEPT Baseline Evaluation Report\n")

    if report.intent_val:
        lines.append("## Intent Classification — Validation Set\n")
        lines.append(f"- **Accuracy**: {report.intent_val.accuracy:.1%}")
        lines.append(
            f"- **Total / Correct**: {report.intent_val.total} / {report.intent_val.correct}"
        )
        if report.intent_val.confusion_pairs:
            lines.append("\n### Top Confusion Pairs\n")
            lines.append("| Ground Truth | Predicted | Count |")
            lines.append("|---|---|---|")
            for gt, pred, count in report.intent_val.confusion_pairs[:10]:
                lines.append(f"| {gt} | {pred} | {count} |")
        lines.append("")

    if report.intent_golden:
        lines.append("## Intent Classification — Golden Tests\n")
        lines.append(f"- **Accuracy**: {report.intent_golden.accuracy:.1%}")
        lines.append(
            f"- **Total / Correct**: "
            f"{report.intent_golden.total} / {report.intent_golden.correct}"
        )
        lines.append("")

    if report.slot_val:
        lines.append("## Slot Filling — Validation Set\n")
        lines.append(f"- **Exact Match**: {report.slot_val.exact_match:.1%}")
        lines.append(f"- **Slot F1**: {report.slot_val.slot_f1:.1%}")
        lines.append(f"- **Total**: {report.slot_val.total}")
        if report.slot_val.worst_intents:
            lines.append("\n### Worst Intents by F1\n")
            lines.append("| Intent | F1 |")
            lines.append("|---|---|")
            for intent, f1 in report.slot_val.worst_intents[:10]:
                lines.append(f"| {intent} | {f1:.1%} |")
        lines.append("")

    if report.slot_golden:
        lines.append("## Slot Filling — Golden Tests\n")
        lines.append(f"- **Exact Match**: {report.slot_golden.exact_match:.1%}")
        lines.append(f"- **Slot F1**: {report.slot_golden.slot_f1:.1%}")
        lines.append(f"- **Total**: {report.slot_golden.total}")
        lines.append("")

    if report.safety_canary_pass_rate is not None:
        lines.append("## Safety\n")
        lines.append(f"- **Canary Pass Rate**: {report.safety_canary_pass_rate:.1%}")
        lines.append("")

    if report.constrained_decoding_validity is not None:
        lines.append("## Constrained Decoding\n")
        lines.append(f"- **Validity Rate**: {report.constrained_decoding_validity:.1%}")
        lines.append("")

    if report.recommendations:
        lines.append("## Recommendations\n")
        for rec in report.recommendations:
            lines.append(f"- {rec}")
        lines.append("")

    return "\n".join(lines)


def save_report(report: BaselineReport, output_dir: str | Path) -> Path:
    """Save evaluation report as JSON + Markdown.

    Args:
        report: The baseline report model.
        output_dir: Directory to write report files.

    Returns:
        Path to the Markdown report file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON
    json_path = output_dir / "baseline_report.json"
    with open(json_path, "w") as f:
        json.dump(report.model_dump(), f, indent=2)

    # Markdown
    md_path = output_dir / "baseline_report.md"
    md_content = generate_report(report)
    with open(md_path, "w") as f:
        f.write(md_content)

    return md_path

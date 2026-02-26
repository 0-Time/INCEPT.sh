"""Forum mining infrastructure for Stack Exchange data dumps.

Parses Stack Exchange XML data dumps (CC-BY-SA 4.0) and extracts
Q&A pairs relevant to Linux command-line tasks.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# Tags that indicate Linux CLI-related questions
_RELEVANT_TAGS = frozenset({
    "bash", "shell", "command-line", "linux", "ubuntu", "debian", "centos",
    "rhel", "fedora", "terminal", "cli", "scripting", "shell-script",
    "permissions", "files", "grep", "find", "sed", "awk", "cron",
    "systemd", "apt", "yum", "dnf", "ssh", "networking", "process",
    "package-management", "filesystems", "mount", "disk-usage",
    "text-processing", "archiving", "tar", "compression", "users",
    "services", "logs", "syslog", "firewall", "iptables",
})

# Patterns for extracting commands from answer bodies
_CODE_BLOCK_PATTERN = re.compile(r"<code>(.*?)</code>", re.DOTALL)
_PRE_BLOCK_PATTERN = re.compile(r"<pre><code>(.*?)</code></pre>", re.DOTALL)

# HTML tag cleanup
_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")

# Commands that indicate a CLI answer
_CLI_INDICATORS = re.compile(
    r"\b(sudo|apt|yum|dnf|systemctl|find|grep|sed|awk|tar|chmod|chown|"
    r"mkdir|rm|cp|mv|ls|cat|head|tail|kill|ps|df|du|mount|cron|ssh|"
    r"wget|curl|ping|netstat|ss|ip|useradd|userdel|service)\b"
)


class ForumExample(BaseModel):
    """A training example extracted from a forum post."""

    question_id: int
    question_title: str
    question_body: str
    answer_body: str
    answer_score: int = 0
    tags: list[str] = Field(default_factory=list)
    extracted_command: str | None = None
    attribution: str = ""


class ForumMiner:
    """Extract CLI-related Q&A pairs from Stack Exchange data dumps.

    Usage:
        miner = ForumMiner()
        miner.load_posts("path/to/Posts.xml")
        examples = miner.extract_examples()
    """

    def __init__(self) -> None:
        self._questions: dict[int, dict[str, Any]] = {}
        self._answers: list[dict[str, Any]] = []

    def load_posts(self, posts_xml_path: str | Path) -> int:
        """Load and parse a Stack Exchange Posts.xml file.

        Returns the number of relevant posts loaded.
        """
        path = Path(posts_xml_path)
        if not path.exists():
            raise FileNotFoundError(f"Posts file not found: {path}")

        count = 0
        for _event, elem in ET.iterparse(str(path), events=("end",)):
            if elem.tag != "row":
                continue

            post_type = elem.get("PostTypeId", "")
            post_id = int(elem.get("Id", "0"))

            if post_type == "1":  # Question
                tags_str = elem.get("Tags", "")
                tags = re.findall(r"<([^>]+)>", tags_str)
                if any(t in _RELEVANT_TAGS for t in tags):
                    self._questions[post_id] = {
                        "id": post_id,
                        "title": elem.get("Title", ""),
                        "body": elem.get("Body", ""),
                        "tags": tags,
                        "score": int(elem.get("Score", "0")),
                    }
                    count += 1

            elif post_type == "2":  # Answer
                parent_id = int(elem.get("ParentId", "0"))
                body = elem.get("Body", "")
                if _CLI_INDICATORS.search(body):
                    self._answers.append({
                        "question_id": parent_id,
                        "body": body,
                        "score": int(elem.get("Score", "0")),
                        "id": post_id,
                    })

            elem.clear()

        return count

    def _extract_commands(self, html_body: str) -> list[str]:
        """Extract shell commands from HTML answer body."""
        commands: list[str] = []

        # Try <pre><code> blocks first (more reliable)
        for match in _PRE_BLOCK_PATTERN.finditer(html_body):
            code = _HTML_TAG_PATTERN.sub("", match.group(1)).strip()
            if code and _CLI_INDICATORS.search(code):
                # Split multi-line code blocks
                for line in code.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#") and _CLI_INDICATORS.search(line):
                        # Remove shell prompts
                        line = re.sub(r"^\$\s*", "", line)
                        line = re.sub(r"^#\s*", "", line)
                        if line:
                            commands.append(line)

        # Fallback to inline <code> blocks
        if not commands:
            for match in _CODE_BLOCK_PATTERN.finditer(html_body):
                code = _HTML_TAG_PATTERN.sub("", match.group(1)).strip()
                if code and _CLI_INDICATORS.search(code) and len(code) < 200:
                    commands.append(code)

        return commands

    def _clean_text(self, html: str) -> str:
        """Remove HTML tags and clean up text."""
        text = _HTML_TAG_PATTERN.sub(" ", html)
        text = re.sub(r"\s+", " ", text).strip()
        # Decode common HTML entities
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')
        text = text.replace("&#39;", "'")
        return text

    def extract_examples(
        self, min_answer_score: int = 2, max_examples: int = 1000
    ) -> list[ForumExample]:
        """Extract training examples from loaded posts.

        Returns ForumExample objects with question, answer, and extracted command.
        """
        examples: list[ForumExample] = []

        # Group answers by question, keep highest-scored
        best_answers: dict[int, dict[str, Any]] = {}
        for answer in self._answers:
            qid = answer["question_id"]
            if qid not in self._questions:
                continue
            if answer["score"] < min_answer_score:
                continue
            if qid not in best_answers or answer["score"] > best_answers[qid]["score"]:
                best_answers[qid] = answer

        for qid, answer in best_answers.items():
            if len(examples) >= max_examples:
                break

            question = self._questions[qid]
            commands = self._extract_commands(answer["body"])

            if not commands:
                continue

            example = ForumExample(
                question_id=qid,
                question_title=question["title"],
                question_body=self._clean_text(question["body"]),
                answer_body=self._clean_text(answer["body"]),
                answer_score=answer["score"],
                tags=question["tags"],
                extracted_command=commands[0],  # Best/first command
                attribution=f"Stack Exchange post #{qid} (CC-BY-SA 4.0)",
            )
            examples.append(example)

        return examples

    def to_training_format(
        self, examples: list[ForumExample]
    ) -> list[dict[str, Any]]:
        """Convert ForumExamples to INCEPT training JSONL format.

        Note: These need manual/automated intent labeling before use.
        """
        records: list[dict[str, Any]] = []
        for i, ex in enumerate(examples):
            records.append({
                "id": f"FM-{i:05d}",
                "source": "forum",
                "license": "CC-BY-SA-4.0",
                "nl_request": ex.question_title,
                "context_line": "debian bash non-root safe",  # Default; needs refinement
                "expected_intent": "",  # Needs labeling
                "expected_slots": {},
                "expected_command": ex.extracted_command or "",
                "tags": ["forum", "stack_exchange"] + ex.tags[:5],
                "attribution": ex.attribution,
            })
        return records

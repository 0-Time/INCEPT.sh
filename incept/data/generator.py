"""Template-based training data generator.

Combines NL templates with slot value pools to produce diverse
training examples in JSONL format.
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any

from incept.data import slot_pools as pools

# Mapping from template slot names to pool sources
# Each entry: slot_name -> (pool_list, is_random_choice)
_SLOT_POOL_MAP: dict[str, list[Any]] = {
    # File system
    "path": pools.PATHS_COMMON,
    "source": pools.PATHS_COMMON + pools.FILE_NAMES,
    "destination": pools.PATHS_COMMON + pools.FILE_NAMES,
    "target": pools.PATHS_COMMON + pools.FILE_NAMES,
    "file": pools.PATHS_CONFIG + pools.FILE_NAMES,
    "file1": pools.PATHS_CONFIG + pools.FILE_NAMES,
    "file2": pools.PATHS_CONFIG + pools.FILE_NAMES,
    "link_name": ["/usr/local/bin/myapp", "/usr/bin/python", "~/bin/tool", "/opt/bin/app"],
    "log_file": pools.PATHS_LOG,
    # Patterns
    "name_pattern": pools.FILE_PATTERNS,
    "pattern": pools.SEARCH_PATTERNS,
    "query": pools.SEARCH_PATTERNS + pools.PACKAGES_DEBIAN,
    "replacement": [p[1] for p in pools.REPLACE_PAIRS],
    # Packages & services
    "package": pools.PACKAGES_DEBIAN,
    "service": pools.SERVICES,
    # Users & groups
    "username": pools.USERNAMES,
    "owner": pools.USERNAMES,
    "group": pools.GROUP_NAMES,
    # Network
    "host": pools.HOSTNAMES,
    "url": pools.URLS,
    "user": pools.USERNAMES,
    "interface": ["eth0", "ens33", "wlan0", "enp0s3", "lo"],
    # Permissions
    "permissions": pools.PERMISSIONS,
    # Sizes & times
    "size_gt": pools.FILE_SIZES,
    "size_lt": pools.FILE_SIZES,
    "mtime": pools.MTIME_DAYS,
    # Scheduling
    "schedule": pools.CRON_SCHEDULES,
    "command": pools.CRON_COMMANDS,
    # Archives
    "archive": pools.ARCHIVE_NAMES,
    "format": pools.ARCHIVE_FORMATS,
    "output": pools.ARCHIVE_NAMES,
    # Process
    "pid": [str(x) for x in range(1000, 50000, 3333)],
    "name": pools.PROCESS_NAMES,
    "signal": pools.SIGNALS,
    "filter": pools.PROCESS_NAMES,
    # Devices
    "device": pools.DEVICES,
    "mount_point": pools.MOUNT_POINTS,
    "filesystem": pools.FILESYSTEMS,
    # Misc
    "type": ["file", "directory", "link"],
    "lines": [str(x) for x in [10, 20, 50, 100, 200, 500]],
    "count": [str(x) for x in [4, 5, 10, 20]],
    "top_n": [str(x) for x in [5, 10, 15, 20]],
    "max_depth": [str(x) for x in [1, 2, 3]],
    "key": ["1", "2", "3", "4"],
    "delimiter": [",", "\\t", ":", "|", ";"],
    "columns": ["1", "1,3", "2,4", "1-3", "2"],
    "port": [str(p) for p in pools.PORTS],
    "since": ["1h", "2h", "6h", "12h", "24h", "1d", "3d", "7d", "today", "yesterday"],
    "component": ["cpu", "memory", "disk", "uptime"],
    "shell": ["/bin/bash", "/bin/zsh", "/bin/sh", "/usr/bin/fish"],
    "groups": ["docker", "sudo", "www-data", "developers", "wheel"],
    "home_dir": ["/home/deploy", "/home/appuser", "/opt/service"],
    "version": ["1.0", "2.0", "latest", "1.2.3"],
    "line_start": ["1", "10", "50", "100"],
    "line_end": ["20", "50", "100", "200"],
    "sort_by": ["time", "size", "name"],
    "perm": ["644", "755", "777"],
}

# Intent categories for tagging
_INTENT_CATEGORY: dict[str, str] = {
    "find_files": "file_ops", "copy_files": "file_ops", "move_files": "file_ops",
    "delete_files": "file_ops", "change_permissions": "file_ops",
    "change_ownership": "file_ops", "create_directory": "file_ops",
    "list_directory": "file_ops", "disk_usage": "file_ops", "view_file": "file_ops",
    "create_symlink": "file_ops", "compare_files": "file_ops",
    "search_text": "text_processing", "replace_text": "text_processing",
    "sort_output": "text_processing", "count_lines": "text_processing",
    "extract_columns": "text_processing", "unique_lines": "text_processing",
    "compress_archive": "archive_ops", "extract_archive": "archive_ops",
    "install_package": "package_mgmt", "remove_package": "package_mgmt",
    "update_packages": "package_mgmt", "search_package": "package_mgmt",
    "start_service": "service_mgmt", "stop_service": "service_mgmt",
    "restart_service": "service_mgmt", "enable_service": "service_mgmt",
    "service_status": "service_mgmt",
    "create_user": "user_mgmt", "delete_user": "user_mgmt", "modify_user": "user_mgmt",
    "view_logs": "log_ops", "follow_logs": "log_ops", "filter_logs": "log_ops",
    "schedule_cron": "scheduling", "list_cron": "scheduling", "remove_cron": "scheduling",
    "network_info": "networking", "test_connectivity": "networking",
    "download_file": "networking", "transfer_file": "networking",
    "ssh_connect": "networking", "port_check": "networking",
    "process_list": "process_mgmt", "kill_process": "process_mgmt",
    "system_info": "process_mgmt",
    "mount_device": "disk_ops", "unmount_device": "disk_ops",
}


def _extract_slots(template: str) -> list[str]:
    """Extract {slot_name} placeholders from a template string."""
    import re

    return re.findall(r"\{(\w+)\}", template)


def _fill_template(
    template: str,
    intent: str,
    rng: random.Random,
    distro: str = "debian",
) -> tuple[str, dict[str, Any]]:
    """Fill a template with random slot values.

    Returns (filled_text, slots_dict).
    """
    slots = _extract_slots(template)
    slot_values: dict[str, Any] = {}

    for slot in slots:
        # Special handling for distro-specific pools
        if slot == "package" and distro == "rhel":
            pool = pools.PACKAGES_RHEL
        elif slot == "package":
            pool = pools.PACKAGES_DEBIAN
        else:
            pool = _SLOT_POOL_MAP.get(slot)  # type: ignore[assignment]

        if pool:
            value = rng.choice(pool)
            slot_values[slot] = value
        else:
            # Fallback: use slot name as placeholder
            slot_values[slot] = f"<{slot}>"

    filled = template.format(**slot_values)
    return filled, slot_values


def _make_id(intent: str, index: int) -> str:
    """Generate a deterministic example ID."""
    return f"TG-{intent}-{index:04d}"


def _pick_context(rng: random.Random, distro: str = "debian") -> str:
    """Pick a random context line for the given distro."""
    if distro == "rhel":
        candidates = [c for c in pools.CONTEXT_LINES if "rhel" in c]
    else:
        candidates = [c for c in pools.CONTEXT_LINES if "debian" in c or "ubuntu" in c]
    return rng.choice(candidates) if candidates else "debian bash non-root safe"


def generate_examples(
    templates: dict[str, list[str]],
    target_count: int = 8000,
    seed: int = 42,
    distro_mix: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Generate training examples from templates.

    Args:
        templates: Mapping of intent -> list of NL template strings.
        target_count: Target number of examples to generate.
        seed: Random seed for reproducibility.
        distro_mix: Distribution of distro families (default: 70% debian, 30% rhel).

    Returns:
        List of JSONL-compatible dicts.
    """
    rng = random.Random(seed)
    if distro_mix is None:
        distro_mix = {"debian": 0.7, "rhel": 0.3}

    # Calculate examples per intent
    num_intents = len(templates)
    if num_intents == 0:
        return []
    base_per_intent = target_count // num_intents
    remainder = target_count % num_intents

    examples: list[dict[str, Any]] = []
    global_idx = 0

    for intent_idx, (intent, intent_templates) in enumerate(sorted(templates.items())):
        if not intent_templates:
            continue

        count = base_per_intent + (1 if intent_idx < remainder else 0)
        category = _INTENT_CATEGORY.get(intent, "unknown")

        for i in range(count):
            # Pick distro
            distro = rng.choices(
                list(distro_mix.keys()),
                weights=list(distro_mix.values()),
                k=1,
            )[0]

            # Pick and fill template
            template = rng.choice(intent_templates)
            nl_text, slot_values = _fill_template(template, intent, rng, distro)
            context = _pick_context(rng, distro)

            example = {
                "id": _make_id(intent, i),
                "source": "template",
                "license": "MIT",
                "nl_request": nl_text,
                "context_line": context,
                "expected_intent": intent,
                "expected_slots": slot_values,
                "tags": [category, "template", distro],
            }
            examples.append(example)
            global_idx += 1

    # Shuffle to mix intents
    rng.shuffle(examples)

    # Re-assign sequential IDs after shuffle
    for i, ex in enumerate(examples):
        ex["id"] = f"TG-{i:05d}"

    return examples


def generate_to_jsonl(
    templates: dict[str, list[str]],
    output_path: str | Path,
    target_count: int = 8000,
    seed: int = 42,
) -> int:
    """Generate training examples and write to JSONL file.

    Returns the number of examples written.
    """
    examples = generate_examples(templates, target_count=target_count, seed=seed)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    return len(examples)


def compute_dataset_hash(path: str | Path) -> str:
    """Compute SHA-256 hash of a JSONL file for integrity checking."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def dataset_statistics(examples: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute statistics over a generated dataset."""
    from collections import Counter

    intent_counts = Counter(ex["expected_intent"] for ex in examples)
    source_counts = Counter(ex.get("source", "unknown") for ex in examples)
    tag_counts: Counter[str] = Counter()
    for ex in examples:
        for tag in ex.get("tags", []):
            tag_counts[tag] += 1

    distro_counts: Counter[str] = Counter()
    for ex in examples:
        tags = ex.get("tags", [])
        for t in tags:
            if t in ("debian", "rhel", "ubuntu"):
                distro_counts[t] += 1

    return {
        "total_examples": len(examples),
        "unique_intents": len(intent_counts),
        "intent_distribution": dict(intent_counts.most_common()),
        "source_distribution": dict(source_counts.most_common()),
        "tag_distribution": dict(tag_counts.most_common(20)),
        "distro_distribution": dict(distro_counts.most_common()),
        "min_per_intent": min(intent_counts.values()) if intent_counts else 0,
        "max_per_intent": max(intent_counts.values()) if intent_counts else 0,
    }

"""Tests for all IR schemas — validates every intent's param model."""

import pytest
from pydantic import ValidationError

from incept.schemas import INTENT_PARAM_REGISTRY, validate_params
from incept.schemas.intents import IntentLabel
from incept.schemas.ir import (
    ClarificationIR,
    ConfidenceScore,
    PipelineIR,
    SingleIR,
)

# --- ConfidenceScore ---


class TestConfidenceScore:
    def test_valid(self) -> None:
        cs = ConfidenceScore(intent=0.95, slots=0.88, composite=0.91)
        assert cs.intent == 0.95

    def test_boundary_values(self) -> None:
        cs = ConfidenceScore(intent=0.0, slots=1.0, composite=0.5)
        assert cs.intent == 0.0
        assert cs.slots == 1.0

    def test_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            ConfidenceScore(intent=1.1, slots=0.5, composite=0.5)
        with pytest.raises(ValidationError):
            ConfidenceScore(intent=-0.1, slots=0.5, composite=0.5)


# --- SingleIR ---


class TestSingleIR:
    def test_valid(self) -> None:
        ir = SingleIR(
            intent=IntentLabel.find_files,
            confidence=ConfidenceScore(intent=0.95, slots=0.88, composite=0.91),
            params={"path": "/var/log", "name_pattern": "*.log"},
        )
        assert ir.type == "single"
        assert ir.intent == IntentLabel.find_files
        assert ir.requires_sudo is False

    def test_defaults(self) -> None:
        ir = SingleIR(
            intent=IntentLabel.install_package,
            confidence=ConfidenceScore(intent=0.9, slots=0.9, composite=0.9),
            params={"package": "nginx"},
            requires_sudo=True,
            defaults_applied=["assume_yes"],
        )
        assert ir.requires_sudo is True
        assert "assume_yes" in ir.defaults_applied

    def test_invalid_intent(self) -> None:
        with pytest.raises(ValidationError):
            SingleIR(
                intent="not_a_real_intent",  # type: ignore[arg-type]
                confidence=ConfidenceScore(intent=0.9, slots=0.9, composite=0.9),
                params={},
            )


# --- PipelineIR ---


class TestPipelineIR:
    def test_valid_sequential(self) -> None:
        step1 = SingleIR(
            intent=IntentLabel.find_files,
            confidence=ConfidenceScore(intent=0.9, slots=0.9, composite=0.9),
            params={"path": "/var/log"},
        )
        step2 = SingleIR(
            intent=IntentLabel.compress_archive,
            confidence=ConfidenceScore(intent=0.9, slots=0.9, composite=0.9),
            params={"source": "/tmp/logs"},
        )
        pipeline = PipelineIR(
            composition="sequential",
            steps=[step1, step2],
            variable_bindings={"$STEP_1_OUTPUT": "file list"},
        )
        assert pipeline.type == "pipeline"
        assert len(pipeline.steps) == 2

    def test_invalid_composition(self) -> None:
        with pytest.raises(ValidationError):
            PipelineIR(
                composition="invalid_type",  # type: ignore[arg-type]
                steps=[],
            )

    def test_all_composition_types(self) -> None:
        step = SingleIR(
            intent=IntentLabel.list_directory,
            confidence=ConfidenceScore(intent=0.9, slots=0.9, composite=0.9),
            params={},
        )
        for comp in ["sequential", "pipe", "independent", "subshell", "xargs"]:
            p = PipelineIR(composition=comp, steps=[step])  # type: ignore[arg-type]
            assert p.composition == comp


# --- ClarificationIR ---


class TestClarificationIR:
    def test_valid(self) -> None:
        ir = ClarificationIR(
            reason="missing_required_param",
            missing_params=["package"],
            question_template="which_package",
            options=["nginx", "apache2"],
        )
        assert ir.type == "clarification"
        assert ir.intent == IntentLabel.CLARIFY

    def test_minimal(self) -> None:
        ir = ClarificationIR(
            reason="ambiguous_intent",
            question_template="clarify_intent",
        )
        assert ir.missing_params == []
        assert ir.options == []


# --- IntentLabel completeness ---


class TestIntentLabel:
    def test_count(self) -> None:
        assert len(IntentLabel) == 52

    def test_special_intents(self) -> None:
        assert IntentLabel.CLARIFY.value == "CLARIFY"
        assert IntentLabel.OUT_OF_SCOPE.value == "OUT_OF_SCOPE"
        assert IntentLabel.UNSAFE_REQUEST.value == "UNSAFE_REQUEST"

    def test_all_intents_in_registry(self) -> None:
        for intent in IntentLabel:
            assert intent in INTENT_PARAM_REGISTRY, f"{intent} missing from registry"


# --- Per-intent param validation ---


# Valid inputs for every intent
_VALID_PARAMS: dict[IntentLabel, dict[str, object]] = {
    IntentLabel.find_files: {"path": "/var/log", "name_pattern": "*.log", "type": "file"},
    IntentLabel.copy_files: {"source": "/a", "destination": "/b", "recursive": True},
    IntentLabel.move_files: {"source": "/a", "destination": "/b"},
    IntentLabel.delete_files: {"target": "/tmp/old", "force": True},
    IntentLabel.change_permissions: {"target": "/etc/app.conf", "permissions": "755"},
    IntentLabel.change_ownership: {"target": "/var/www", "owner": "www-data", "group": "www-data"},
    IntentLabel.create_directory: {"path": "/tmp/newdir", "parents": True},
    IntentLabel.list_directory: {"path": "/home", "long_format": True, "all_files": True},
    IntentLabel.disk_usage: {"path": "/var", "human_readable": True, "max_depth": 2},
    IntentLabel.view_file: {"file": "/etc/hosts", "lines": 20},
    IntentLabel.create_symlink: {"target": "/usr/bin/python3", "link_name": "/usr/bin/python"},
    IntentLabel.compare_files: {"file1": "/a.txt", "file2": "/b.txt", "context_lines": 3},
    IntentLabel.search_text: {"pattern": "error", "path": "/var/log", "recursive": True},
    IntentLabel.replace_text: {"pattern": "old", "replacement": "new", "file": "/etc/config"},
    IntentLabel.sort_output: {"input_file": "/tmp/data.txt", "numeric": True},
    IntentLabel.count_lines: {"input_file": "/etc/passwd", "mode": "lines"},
    IntentLabel.extract_columns: {"field_spec": "1,3", "delimiter": ":"},
    IntentLabel.unique_lines: {"input_file": "/tmp/data.txt", "count": True},
    IntentLabel.compress_archive: {"source": "/var/log", "format": "tar.gz"},
    IntentLabel.extract_archive: {"source": "/tmp/archive.tar.gz", "destination": "/tmp/out"},
    IntentLabel.install_package: {"package": "nginx", "assume_yes": True},
    IntentLabel.remove_package: {"package": "nginx", "purge_config": True},
    IntentLabel.update_packages: {"upgrade_all": True},
    IntentLabel.search_package: {"query": "nginx"},
    IntentLabel.start_service: {"service_name": "nginx"},
    IntentLabel.stop_service: {"service_name": "nginx"},
    IntentLabel.restart_service: {"service_name": "nginx"},
    IntentLabel.enable_service: {"service_name": "nginx"},
    IntentLabel.service_status: {"service_name": "nginx"},
    IntentLabel.create_user: {"username": "deploy", "shell": "/bin/bash", "groups": ["docker"]},
    IntentLabel.delete_user: {"username": "olduser", "remove_home": True},
    IntentLabel.modify_user: {"username": "deploy", "add_groups": ["sudo"]},
    IntentLabel.view_logs: {"unit": "nginx", "lines": 100},
    IntentLabel.follow_logs: {"unit": "nginx"},
    IntentLabel.filter_logs: {"pattern": "error", "unit": "nginx"},
    IntentLabel.schedule_cron: {"schedule": "0 2 * * *", "command": "/usr/local/bin/backup.sh"},
    IntentLabel.list_cron: {"user": "root"},
    IntentLabel.remove_cron: {"job_id_or_pattern": "backup"},
    IntentLabel.network_info: {"interface": "eth0"},
    IntentLabel.test_connectivity: {"host": "google.com", "count": 4},
    IntentLabel.download_file: {"url": "https://example.com/file.tar.gz"},
    IntentLabel.transfer_file: {"source": "/local/file", "destination": "user@host:/remote/"},
    IntentLabel.ssh_connect: {"host": "server.example.com", "user": "deploy", "port": 22},
    IntentLabel.port_check: {"port": 8080, "host": "localhost"},
    IntentLabel.process_list: {"filter": "python", "sort_by": "cpu"},
    IntentLabel.kill_process: {"target": "1234", "signal": "SIGTERM"},
    IntentLabel.system_info: {"info_type": "all"},
    IntentLabel.mount_device: {"device": "/dev/sdb1", "mount_point": "/mnt/data"},
    IntentLabel.unmount_device: {"mount_point": "/mnt/data"},
    IntentLabel.CLARIFY: {"reason": "ambiguous_intent", "template_key": "clarify_intent"},
    IntentLabel.OUT_OF_SCOPE: {"reason": "Not a Linux command"},
    IntentLabel.UNSAFE_REQUEST: {"reason": "Destructive operation"},
}

# Invalid inputs for selected intents
_INVALID_PARAMS: list[tuple[IntentLabel, dict[str, object]]] = [
    # Missing required field
    (IntentLabel.copy_files, {"source": "/a"}),  # missing destination
    (IntentLabel.move_files, {}),  # missing both
    (IntentLabel.delete_files, {}),  # missing target
    (IntentLabel.replace_text, {"pattern": "old"}),  # missing replacement and file
    (IntentLabel.install_package, {}),  # missing package
    (IntentLabel.start_service, {}),  # missing service_name
    (IntentLabel.create_user, {}),  # missing username
    (IntentLabel.filter_logs, {}),  # missing pattern
    (IntentLabel.schedule_cron, {"schedule": "* * * * *"}),  # missing command
    (IntentLabel.test_connectivity, {}),  # missing host
    (IntentLabel.kill_process, {}),  # missing target
    (IntentLabel.mount_device, {"device": "/dev/sdb1"}),  # missing mount_point
    (IntentLabel.transfer_file, {"source": "/local"}),  # missing destination
    (IntentLabel.ssh_connect, {}),  # missing host
    (IntentLabel.remove_cron, {}),  # missing job_id_or_pattern
    # Invalid enum values
    (IntentLabel.count_lines, {"mode": "paragraphs"}),
    (IntentLabel.compress_archive, {"source": "/a", "format": "rar"}),
    (IntentLabel.system_info, {"info_type": "gpu"}),
    (IntentLabel.find_files, {"type": "socket"}),
    (IntentLabel.CLARIFY, {"reason": "bored", "template_key": "clarify_intent"}),
    # Invalid field constraints
    (IntentLabel.compare_files, {"file1": "/a", "file2": "/b", "context_lines": -1}),
    (IntentLabel.test_connectivity, {"host": "x", "count": 0}),
    (IntentLabel.port_check, {"port": 99999}),
]


class TestParamSchemas:
    @pytest.mark.parametrize("intent", list(IntentLabel))
    def test_valid_params(self, intent: IntentLabel) -> None:
        params = _VALID_PARAMS[intent]
        model = validate_params(intent, params)
        assert model is not None

    @pytest.mark.parametrize("intent,params", _INVALID_PARAMS)
    def test_invalid_params(self, intent: IntentLabel, params: dict[str, object]) -> None:
        with pytest.raises(ValidationError):
            validate_params(intent, params)

    def test_defaults_applied(self) -> None:
        """Params with all-optional fields should accept empty dict."""
        for intent in [
            IntentLabel.find_files,
            IntentLabel.list_directory,
            IntentLabel.disk_usage,
            IntentLabel.sort_output,
            IntentLabel.count_lines,
            IntentLabel.unique_lines,
            IntentLabel.update_packages,
            IntentLabel.view_logs,
            IntentLabel.follow_logs,
            IntentLabel.list_cron,
            IntentLabel.network_info,
            IntentLabel.port_check,
            IntentLabel.process_list,
            IntentLabel.system_info,
            IntentLabel.OUT_OF_SCOPE,
            IntentLabel.UNSAFE_REQUEST,
        ]:
            model = validate_params(intent, {})
            assert model is not None

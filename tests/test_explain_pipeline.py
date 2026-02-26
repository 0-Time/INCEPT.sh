"""Tests for the explain pipeline (command → structured NL explanation)."""

from __future__ import annotations

from incept.explain.pipeline import ExplainResponse, run_explain_pipeline


class TestRunExplainPipeline:
    """Core explain pipeline tests."""

    def test_apt_install(self) -> None:
        resp = run_explain_pipeline("apt-get install nginx")
        assert isinstance(resp, ExplainResponse)
        assert resp.intent == "install_package"
        assert resp.explanation
        assert resp.risk_level == "safe"

    def test_apt_install_with_yes(self) -> None:
        resp = run_explain_pipeline("apt-get install -y nginx")
        assert resp.intent == "install_package"
        assert "nginx" in resp.explanation.lower() or "install" in resp.explanation.lower()

    def test_dnf_install(self) -> None:
        resp = run_explain_pipeline("dnf install -y httpd")
        assert resp.intent == "install_package"

    def test_systemctl_restart(self) -> None:
        resp = run_explain_pipeline("systemctl restart nginx")
        assert resp.intent == "restart_service"

    def test_docker_run(self) -> None:
        resp = run_explain_pipeline("docker run -d nginx")
        assert resp.intent == "docker_run"

    def test_find_command(self) -> None:
        resp = run_explain_pipeline("find /tmp -name '*.log' -type f")
        assert resp.intent == "find_files"

    def test_grep_command(self) -> None:
        resp = run_explain_pipeline("grep -r error /var/log")
        assert resp.intent == "search_text"

    def test_git_commit(self) -> None:
        resp = run_explain_pipeline("git commit -m 'fix bug'")
        assert resp.intent == "git_commit"

    def test_unknown_command(self) -> None:
        resp = run_explain_pipeline("frobnicator --quux")
        assert resp.intent is None
        assert "unrecognized" in resp.explanation.lower() or "unknown" in resp.explanation.lower()

    def test_empty_string_error(self) -> None:
        resp = run_explain_pipeline("")
        assert resp.intent is None

    def test_sudo_prefix_handled(self) -> None:
        resp = run_explain_pipeline("sudo systemctl start nginx")
        assert resp.intent == "start_service"

    def test_dangerous_command_flagged(self) -> None:
        resp = run_explain_pipeline("rm -rf /")
        assert resp.risk_level in ("dangerous", "blocked")

    def test_response_has_command_field(self) -> None:
        resp = run_explain_pipeline("apt-get install nginx")
        assert resp.command == "apt-get install nginx"

    def test_response_has_params(self) -> None:
        resp = run_explain_pipeline("apt-get install nginx")
        assert resp.params.get("package") == "nginx"

    def test_curl_download(self) -> None:
        resp = run_explain_pipeline("curl -O https://example.com/file.tar.gz")
        assert resp.intent == "download_file"

    def test_tar_extract(self) -> None:
        resp = run_explain_pipeline("tar -xzf archive.tar.gz")
        assert resp.intent == "extract_archive"

    def test_ssh_keygen(self) -> None:
        resp = run_explain_pipeline("ssh-keygen -t ed25519")
        assert resp.intent == "generate_ssh_key"

    def test_brew_install(self) -> None:
        resp = run_explain_pipeline("brew install wget")
        assert resp.intent == "install_package"

    def test_ufw_allow(self) -> None:
        resp = run_explain_pipeline("ufw allow 80")
        assert resp.intent == "firewall_allow"

    def test_pacman_install(self) -> None:
        resp = run_explain_pipeline("pacman -S nginx")
        assert resp.intent == "install_package"

    def test_pipe_command(self) -> None:
        resp = run_explain_pipeline("grep error /var/log/syslog | head -20")
        assert resp.intent == "search_text"


class TestExplainResponseModel:
    """ExplainResponse Pydantic model."""

    def test_default_values(self) -> None:
        resp = ExplainResponse(command="test", explanation="test explanation")
        assert resp.intent is None
        assert resp.risk_level == "safe"
        assert resp.params == {}
        assert resp.flag_explanations == {}
        assert resp.side_effects == []

    def test_full_response(self) -> None:
        resp = ExplainResponse(
            command="apt-get install nginx",
            intent="install_package",
            explanation="Install the nginx package",
            flag_explanations={"-y": "auto-confirm"},
            side_effects=["Downloads package"],
            risk_level="safe",
            params={"package": "nginx"},
        )
        assert resp.intent == "install_package"
        assert len(resp.flag_explanations) == 1
        assert len(resp.side_effects) == 1

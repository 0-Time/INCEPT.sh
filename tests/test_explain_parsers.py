"""Tests for inverse command parsers (command → intent + params)."""

from __future__ import annotations

from incept.explain.parsers import (
    parse_apt_get,
    parse_brew,
    parse_crontab,
    parse_curl,
    parse_dnf,
    parse_docker,
    parse_find,
    parse_git,
    parse_grep,
    parse_pacman,
    parse_sed,
    parse_ssh,
    parse_systemctl,
    parse_tar,
    parse_ufw,
    parse_wget,
    parse_zypper,
)
from incept.explain.registry import parse_command

# ===================================================================
# apt-get parser
# ===================================================================


class TestAptGetParser:
    def test_install(self) -> None:
        r = parse_apt_get("apt-get install nginx")
        assert r is not None
        assert r.intent == "install_package"
        assert r.params["package"] == "nginx"

    def test_install_with_yes(self) -> None:
        r = parse_apt_get("apt-get install -y curl")
        assert r is not None
        assert r.params["package"] == "curl"

    def test_remove(self) -> None:
        r = parse_apt_get("apt-get remove nginx")
        assert r is not None
        assert r.intent == "remove_package"

    def test_purge(self) -> None:
        r = parse_apt_get("apt-get purge nginx")
        assert r is not None
        assert r.intent == "remove_package"
        assert r.params.get("purge_config") is True

    def test_update(self) -> None:
        r = parse_apt_get("apt-get update")
        assert r is not None
        assert r.intent == "update_packages"

    def test_upgrade(self) -> None:
        r = parse_apt_get("apt-get upgrade")
        assert r is not None
        assert r.intent == "update_packages"

    def test_non_apt(self) -> None:
        assert parse_apt_get("dnf install nginx") is None


# ===================================================================
# dnf parser
# ===================================================================


class TestDnfParser:
    def test_install(self) -> None:
        r = parse_dnf("dnf install nginx")
        assert r is not None
        assert r.intent == "install_package"

    def test_remove(self) -> None:
        r = parse_dnf("dnf remove nginx")
        assert r is not None
        assert r.intent == "remove_package"

    def test_upgrade(self) -> None:
        r = parse_dnf("dnf upgrade")
        assert r is not None
        assert r.intent == "update_packages"

    def test_search(self) -> None:
        r = parse_dnf("dnf search nginx")
        assert r is not None
        assert r.intent == "search_package"


# ===================================================================
# pacman parser
# ===================================================================


class TestPacmanParser:
    def test_install(self) -> None:
        r = parse_pacman("pacman -S nginx")
        assert r is not None
        assert r.intent == "install_package"

    def test_remove(self) -> None:
        r = parse_pacman("pacman -R nginx")
        assert r is not None
        assert r.intent == "remove_package"

    def test_sync_upgrade(self) -> None:
        r = parse_pacman("pacman -Syu")
        assert r is not None
        assert r.intent == "update_packages"

    def test_search(self) -> None:
        r = parse_pacman("pacman -Ss nginx")
        assert r is not None
        assert r.intent == "search_package"


# ===================================================================
# zypper parser
# ===================================================================


class TestZypperParser:
    def test_install(self) -> None:
        r = parse_zypper("zypper install nginx")
        assert r is not None
        assert r.intent == "install_package"

    def test_remove(self) -> None:
        r = parse_zypper("zypper remove nginx")
        assert r is not None
        assert r.intent == "remove_package"


# ===================================================================
# brew parser
# ===================================================================


class TestBrewParser:
    def test_install(self) -> None:
        r = parse_brew("brew install nginx")
        assert r is not None
        assert r.intent == "install_package"
        assert r.params["package"] == "nginx"

    def test_uninstall(self) -> None:
        r = parse_brew("brew uninstall nginx")
        assert r is not None
        assert r.intent == "remove_package"

    def test_update(self) -> None:
        r = parse_brew("brew update")
        assert r is not None
        assert r.intent == "update_packages"

    def test_search(self) -> None:
        r = parse_brew("brew search nginx")
        assert r is not None
        assert r.intent == "search_package"

    def test_services_start(self) -> None:
        r = parse_brew("brew services start nginx")
        assert r is not None
        assert r.intent == "start_service"


# ===================================================================
# systemctl parser
# ===================================================================


class TestSystemctlParser:
    def test_start(self) -> None:
        r = parse_systemctl("systemctl start nginx")
        assert r is not None
        assert r.intent == "start_service"
        assert r.params["service_name"] == "nginx"

    def test_stop(self) -> None:
        r = parse_systemctl("systemctl stop nginx")
        assert r is not None
        assert r.intent == "stop_service"

    def test_restart(self) -> None:
        r = parse_systemctl("systemctl restart nginx")
        assert r is not None
        assert r.intent == "restart_service"

    def test_enable(self) -> None:
        r = parse_systemctl("systemctl enable nginx")
        assert r is not None
        assert r.intent == "enable_service"

    def test_status(self) -> None:
        r = parse_systemctl("systemctl status nginx")
        assert r is not None
        assert r.intent == "service_status"


# ===================================================================
# find parser
# ===================================================================


class TestFindParser:
    def test_basic(self) -> None:
        r = parse_find("find /var/log -name '*.log'")
        assert r is not None
        assert r.intent == "find_files"
        assert r.params["path"] == "/var/log"

    def test_with_type(self) -> None:
        r = parse_find("find . -type f -name '*.py'")
        assert r is not None
        assert r.params.get("type") == "f"


# ===================================================================
# grep parser
# ===================================================================


class TestGrepParser:
    def test_basic(self) -> None:
        r = parse_grep("grep error /var/log/syslog")
        assert r is not None
        assert r.intent == "search_text"
        assert r.params["pattern"] == "error"

    def test_recursive(self) -> None:
        r = parse_grep("grep -r 'TODO' src/")
        assert r is not None
        assert r.params.get("recursive") is True

    def test_case_insensitive(self) -> None:
        r = parse_grep("grep -i warning /var/log")
        assert r is not None
        assert r.params.get("ignore_case") is True


# ===================================================================
# sed parser
# ===================================================================


class TestSedParser:
    def test_substitute(self) -> None:
        r = parse_sed("sed -i 's/foo/bar/g' file.txt")
        assert r is not None
        assert r.intent == "replace_text"

    def test_no_match(self) -> None:
        assert parse_sed("echo hello") is None


# ===================================================================
# tar parser
# ===================================================================


class TestTarParser:
    def test_create(self) -> None:
        r = parse_tar("tar -czf archive.tar.gz dir/")
        assert r is not None
        assert r.intent == "compress_archive"

    def test_extract(self) -> None:
        r = parse_tar("tar -xzf archive.tar.gz")
        assert r is not None
        assert r.intent == "extract_archive"


# ===================================================================
# docker parser
# ===================================================================


class TestDockerParser:
    def test_run(self) -> None:
        r = parse_docker("docker run nginx")
        assert r is not None
        assert r.intent == "docker_run"

    def test_ps(self) -> None:
        r = parse_docker("docker ps")
        assert r is not None
        assert r.intent == "docker_ps"

    def test_stop(self) -> None:
        r = parse_docker("docker stop my-container")
        assert r is not None
        assert r.intent == "docker_stop"

    def test_logs(self) -> None:
        r = parse_docker("docker logs my-container")
        assert r is not None
        assert r.intent == "docker_logs"

    def test_build(self) -> None:
        r = parse_docker("docker build -t myimage .")
        assert r is not None
        assert r.intent == "docker_build"

    def test_exec(self) -> None:
        r = parse_docker("docker exec -it container bash")
        assert r is not None
        assert r.intent == "docker_exec"


# ===================================================================
# git parser
# ===================================================================


class TestGitParser:
    def test_status(self) -> None:
        r = parse_git("git status")
        assert r is not None
        assert r.intent == "git_status"

    def test_commit(self) -> None:
        r = parse_git("git commit -m 'fix bug'")
        assert r is not None
        assert r.intent == "git_commit"

    def test_push(self) -> None:
        r = parse_git("git push origin main")
        assert r is not None
        assert r.intent == "git_push"

    def test_pull(self) -> None:
        r = parse_git("git pull")
        assert r is not None
        assert r.intent == "git_pull"

    def test_log(self) -> None:
        r = parse_git("git log --oneline")
        assert r is not None
        assert r.intent == "git_log"

    def test_diff(self) -> None:
        r = parse_git("git diff --staged")
        assert r is not None
        assert r.intent == "git_diff"

    def test_branch(self) -> None:
        r = parse_git("git branch -a")
        assert r is not None
        assert r.intent == "git_branch"


# ===================================================================
# ssh parser
# ===================================================================


class TestSSHParser:
    def test_keygen(self) -> None:
        r = parse_ssh("ssh-keygen -t ed25519")
        assert r is not None
        assert r.intent == "generate_ssh_key"

    def test_copy_id(self) -> None:
        r = parse_ssh("ssh-copy-id user@host")
        assert r is not None
        assert r.intent == "copy_ssh_key"

    def test_connect(self) -> None:
        r = parse_ssh("ssh user@host")
        assert r is not None
        assert r.intent == "ssh_connect"


# ===================================================================
# ufw parser
# ===================================================================


class TestUfwParser:
    def test_allow(self) -> None:
        r = parse_ufw("ufw allow 80")
        assert r is not None
        assert r.intent == "firewall_allow"
        assert r.params["port"] == "80"

    def test_deny(self) -> None:
        r = parse_ufw("ufw deny 22")
        assert r is not None
        assert r.intent == "firewall_deny"

    def test_status(self) -> None:
        r = parse_ufw("ufw status")
        assert r is not None
        assert r.intent == "firewall_list"


# ===================================================================
# curl parser
# ===================================================================


class TestCurlParser:
    def test_download(self) -> None:
        r = parse_curl("curl -O https://example.com/file.tar.gz")
        assert r is not None
        assert r.intent == "download_file"

    def test_output(self) -> None:
        r = parse_curl("curl -o output.txt https://example.com/data")
        assert r is not None
        assert r.params.get("output_path") == "output.txt"


# ===================================================================
# wget parser
# ===================================================================


class TestWgetParser:
    def test_download(self) -> None:
        r = parse_wget("wget https://example.com/file.tar.gz")
        assert r is not None
        assert r.intent == "download_file"


# ===================================================================
# crontab parser
# ===================================================================


class TestCrontabParser:
    def test_list(self) -> None:
        r = parse_crontab("crontab -l")
        assert r is not None
        assert r.intent == "list_cron"

    def test_edit(self) -> None:
        r = parse_crontab("crontab -e")
        assert r is not None
        assert r.intent == "schedule_cron"


# ===================================================================
# Registry integration
# ===================================================================


class TestRegistry:
    """parse_command dispatches to the correct parser."""

    def test_apt_get(self) -> None:
        r = parse_command("apt-get install nginx")
        assert r is not None
        assert r.intent == "install_package"

    def test_sudo_stripped(self) -> None:
        r = parse_command("sudo apt-get install nginx")
        assert r is not None
        assert r.intent == "install_package"

    def test_unrecognized_returns_none(self) -> None:
        assert parse_command("some_unknown_command --flag") is None

    def test_empty_string(self) -> None:
        assert parse_command("") is None

    def test_systemctl(self) -> None:
        r = parse_command("systemctl restart nginx")
        assert r is not None
        assert r.intent == "restart_service"

    def test_docker(self) -> None:
        r = parse_command("docker run -d nginx")
        assert r is not None
        assert r.intent == "docker_run"

    def test_git(self) -> None:
        r = parse_command("git push origin main")
        assert r is not None
        assert r.intent == "git_push"

    def test_find(self) -> None:
        r = parse_command("find /tmp -name '*.log'")
        assert r is not None
        assert r.intent == "find_files"

    def test_pipe_command_first_part(self) -> None:
        r = parse_command("grep error /var/log/syslog | head -20")
        assert r is not None
        assert r.intent == "search_text"

    def test_brew(self) -> None:
        r = parse_command("brew install wget")
        assert r is not None
        assert r.intent == "install_package"

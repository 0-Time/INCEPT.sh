"""Tests for compiler core modules: quoting, router, and composition."""

from __future__ import annotations

import shlex
from typing import Any

import pytest

from incept.compiler.composition import compose_commands, resolve_variable_bindings
from incept.compiler.quoting import ansi_c_quote, needs_ansi_c_quoting, quote_value
from incept.compiler.router import CompileResult, IntentRouter
from incept.core.context import EnvironmentContext
from incept.schemas.intents import IntentLabel
from incept.schemas.ir import (
    ClarificationIR,
    ConfidenceScore,
    PipelineIR,
    SingleIR,
)

# ---------------------------------------------------------------------------
# Helpers / factories
# ---------------------------------------------------------------------------

def _confidence(value: float = 0.9) -> ConfidenceScore:
    """Factory for a uniform confidence score."""
    return ConfidenceScore(intent=value, slots=value, composite=value)


def _single_ir(
    intent: IntentLabel = IntentLabel.list_directory,
    params: dict[str, object] | None = None,
    requires_sudo: bool = False,
) -> SingleIR:
    """Factory for a minimal SingleIR."""
    return SingleIR(
        intent=intent,
        confidence=_confidence(),
        params=params or {},
        requires_sudo=requires_sudo,
    )


def _pipeline_ir(
    steps: list[SingleIR],
    composition: str = "sequential",
    variable_bindings: dict[str, str] | None = None,
) -> PipelineIR:
    """Factory for a minimal PipelineIR."""
    return PipelineIR(
        composition=composition,  # type: ignore[arg-type]
        steps=steps,
        variable_bindings=variable_bindings or {},
    )


def _echo_compiler(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Trivial compiler that echoes a 'cmd' param or a fixed string."""
    return params.get("cmd", "echo hello")


def _default_ctx(**overrides: Any) -> EnvironmentContext:
    """Factory for EnvironmentContext with optional field overrides."""
    return EnvironmentContext(**overrides)


# ===================================================================
# QUOTING MODULE
# ===================================================================


class TestNeedsAnsiCQuoting:
    """Tests for needs_ansi_c_quoting()."""

    @pytest.mark.parametrize(
        "value",
        [
            "hello",
            "simple text",
            "/var/log/syslog",
            "*.log",
            "file with spaces",
            "UPPER_CASE",
            "123",
            "",
        ],
        ids=[
            "plain_alpha",
            "spaces",
            "path",
            "glob",
            "mixed_spaces",
            "uppercase",
            "digits",
            "empty",
        ],
    )
    def test_returns_false_for_normal_text(self, value: str) -> None:
        assert needs_ansi_c_quoting(value) is False

    @pytest.mark.parametrize(
        "value,description",
        [
            ("\n", "newline"),
            ("\t", "tab"),
            ("\r", "carriage_return"),
            ("\a", "bell"),
            ("\b", "backspace"),
            ("\f", "form_feed"),
            ("\v", "vertical_tab"),
            ("\x01", "SOH_control"),
            ("\x1f", "US_control"),
            ("\x7f", "DEL"),
            ("hello\nworld", "embedded_newline"),
            ("col1\tcol2", "embedded_tab"),
        ],
    )
    def test_returns_true_for_control_characters(
        self, value: str, description: str
    ) -> None:
        assert needs_ansi_c_quoting(value) is True

    def test_mixed_normal_and_control(self) -> None:
        assert needs_ansi_c_quoting("before\x00after") is True

    def test_unicode_no_control(self) -> None:
        assert needs_ansi_c_quoting("cafe\u0301") is False

    def test_high_ascii_not_flagged(self) -> None:
        # Characters above 0x7F (except 0x7F itself) should NOT be flagged
        assert needs_ansi_c_quoting("\x80") is False
        assert needs_ansi_c_quoting("\xff") is False


class TestAnsiCQuote:
    """Tests for ansi_c_quote() -- bash $'...' quoting."""

    def test_plain_string(self) -> None:
        assert ansi_c_quote("hello") == "$'hello'"

    def test_single_quote_escaped(self) -> None:
        assert ansi_c_quote("it's") == "$'it\\'s'"

    def test_backslash_escaped(self) -> None:
        assert ansi_c_quote("a\\b") == "$'a\\\\b'"

    @pytest.mark.parametrize(
        "char,expected_escape",
        [
            ("\n", "\\n"),
            ("\t", "\\t"),
            ("\r", "\\r"),
            ("\a", "\\a"),
            ("\b", "\\b"),
            ("\f", "\\f"),
            ("\v", "\\v"),
        ],
        ids=["newline", "tab", "cr", "bell", "backspace", "formfeed", "vtab"],
    )
    def test_named_escape_sequences(self, char: str, expected_escape: str) -> None:
        result = ansi_c_quote(char)
        assert result == f"$'{expected_escape}'"

    @pytest.mark.parametrize(
        "code",
        [0x01, 0x02, 0x0E, 0x1F, 0x7F],
        ids=["0x01", "0x02", "0x0E", "0x1F", "DEL"],
    )
    def test_hex_escape_for_other_control_chars(self, code: int) -> None:
        ch = chr(code)
        result = ansi_c_quote(ch)
        assert result == f"$'\\x{code:02x}'"

    def test_mixed_content(self) -> None:
        result = ansi_c_quote("line1\nline2\ttab")
        assert result == "$'line1\\nline2\\ttab'"

    def test_empty_string(self) -> None:
        assert ansi_c_quote("") == "$''"

    def test_unicode_passes_through(self) -> None:
        # Non-control unicode chars are passed through unchanged
        result = ansi_c_quote("hello")
        assert result == "$'hello'"

    def test_multiple_escapes_combined(self) -> None:
        result = ansi_c_quote("a'b\\c\nd")
        assert result == "$'a\\'b\\\\c\\nd'"


class TestQuoteValue:
    """Tests for quote_value() -- the main quoting entry point."""

    # --- Empty string ---

    def test_empty_string_returns_empty_quotes(self) -> None:
        assert quote_value("") == "''"

    def test_empty_string_any_shell(self) -> None:
        assert quote_value("", shell="sh") == "''"
        assert quote_value("", shell="zsh") == "''"

    # --- Simple alphanumeric ---

    @pytest.mark.parametrize(
        "value",
        ["hello", "test123", "simple"],
    )
    def test_simple_alphanumeric_unquoted(self, value: str) -> None:
        # shlex.quote returns simple strings unquoted
        result = quote_value(value)
        assert result == shlex.quote(value)

    # --- Spaces ---

    def test_value_with_spaces_is_quoted(self) -> None:
        result = quote_value("hello world")
        assert result == "'hello world'"

    def test_path_with_spaces(self) -> None:
        result = quote_value("/home/user/my documents")
        assert result == "'/home/user/my documents'"

    # --- Single quotes in value ---

    def test_single_quote_in_value(self) -> None:
        result = quote_value("it's")
        expected = shlex.quote("it's")
        assert result == expected

    def test_multiple_single_quotes(self) -> None:
        result = quote_value("it's a 'test'")
        expected = shlex.quote("it's a 'test'")
        assert result == expected

    # --- Double quotes ---

    def test_double_quotes_in_value(self) -> None:
        result = quote_value('say "hello"')
        expected = shlex.quote('say "hello"')
        assert result == expected

    # --- Backticks and dollar signs ---

    def test_backtick_in_value(self) -> None:
        result = quote_value("run `cmd`")
        expected = shlex.quote("run `cmd`")
        assert result == expected

    def test_dollar_sign_in_value(self) -> None:
        result = quote_value("$HOME/path")
        expected = shlex.quote("$HOME/path")
        assert result == expected

    def test_dollar_paren_in_value(self) -> None:
        result = quote_value("$(whoami)")
        expected = shlex.quote("$(whoami)")
        assert result == expected

    # --- Control characters with bash shell ---

    def test_newline_bash_uses_ansi_c(self) -> None:
        result = quote_value("line1\nline2", shell="bash")
        assert result == "$'line1\\nline2'"

    def test_tab_bash_uses_ansi_c(self) -> None:
        result = quote_value("col1\tcol2", shell="bash")
        assert result == "$'col1\\tcol2'"

    def test_carriage_return_bash(self) -> None:
        result = quote_value("text\rmore", shell="bash")
        assert result == "$'text\\rmore'"

    def test_mixed_control_chars_bash(self) -> None:
        result = quote_value("a\nb\tc", shell="bash")
        assert result == "$'a\\nb\\tc'"

    # --- Control characters with zsh shell ---

    def test_newline_zsh_uses_ansi_c(self) -> None:
        result = quote_value("line1\nline2", shell="zsh")
        assert result == "$'line1\\nline2'"

    # --- Control characters with sh shell ---

    def test_newline_sh_uses_shlex(self) -> None:
        result = quote_value("line1\nline2", shell="sh")
        expected = shlex.quote("line1\nline2")
        assert result == expected
        # shlex.quote wraps in single quotes, does NOT use $'...'
        assert not result.startswith("$'")

    def test_tab_sh_uses_shlex(self) -> None:
        result = quote_value("col1\tcol2", shell="sh")
        expected = shlex.quote("col1\tcol2")
        assert result == expected

    # --- Glob characters ---

    def test_asterisk_quoted(self) -> None:
        result = quote_value("*.log")
        expected = shlex.quote("*.log")
        assert result == expected

    def test_question_mark_quoted(self) -> None:
        result = quote_value("file?.txt")
        expected = shlex.quote("file?.txt")
        assert result == expected

    # --- Unicode ---

    def test_unicode_accented(self) -> None:
        result = quote_value("cafe\u0301")
        expected = shlex.quote("cafe\u0301")
        assert result == expected

    def test_unicode_emoji(self) -> None:
        # Emoji should go through shlex.quote, not ANSI-C
        result = quote_value("hello world")
        expected = shlex.quote("hello world")
        assert result == expected

    def test_cjk_characters(self) -> None:
        result = quote_value("file name")
        expected = shlex.quote("file name")
        assert result == expected

    # --- Shell metacharacters ---

    @pytest.mark.parametrize(
        "value",
        ["|", "&", ";", "<", ">", "(", ")", "||", "&&", ">>"],
        ids=["pipe", "amp", "semi", "lt", "gt", "lparen", "rparen", "or", "and", "append"],
    )
    def test_shell_metacharacters_quoted(self, value: str) -> None:
        result = quote_value(value)
        expected = shlex.quote(value)
        assert result == expected
        # Must not be returned bare
        assert result != value or value.isalnum()

    # --- Default shell parameter ---

    def test_default_shell_is_bash(self) -> None:
        # With a newline, default shell should use ANSI-C quoting
        result = quote_value("a\nb")
        assert result.startswith("$'")

    # --- Compound edge cases ---

    def test_value_with_all_specials(self) -> None:
        value = "it's a \"test\" with $VAR and `cmd`"
        result = quote_value(value)
        expected = shlex.quote(value)
        assert result == expected

    def test_only_whitespace(self) -> None:
        result = quote_value("   ")
        expected = shlex.quote("   ")
        assert result == expected

    def test_very_long_string(self) -> None:
        value = "a" * 10000
        result = quote_value(value)
        assert result == shlex.quote(value)

    def test_null_byte_bash(self) -> None:
        # \x00 is a control char (ord < 0x20)
        result = quote_value("\x00", shell="bash")
        assert result == "$'\\x00'"

    def test_del_char_bash(self) -> None:
        result = quote_value("\x7f", shell="bash")
        assert result == "$'\\x7f'"

    def test_backslash_only(self) -> None:
        result = quote_value("\\")
        expected = shlex.quote("\\")
        assert result == expected


# ===================================================================
# COMPILE RESULT
# ===================================================================


class TestCompileResult:
    """Tests for CompileResult data class."""

    def test_str_without_sudo(self) -> None:
        cr = CompileResult(command="ls -la", requires_sudo=False)
        assert str(cr) == "ls -la"

    def test_str_with_sudo(self) -> None:
        cr = CompileResult(command="systemctl restart nginx", requires_sudo=True)
        assert str(cr) == "sudo systemctl restart nginx"

    def test_full_command_without_sudo(self) -> None:
        cr = CompileResult(command="echo hi")
        assert cr.full_command == "echo hi"

    def test_full_command_with_sudo(self) -> None:
        cr = CompileResult(command="apt install nginx", requires_sudo=True)
        assert cr.full_command == "sudo apt install nginx"

    def test_warnings_default_empty(self) -> None:
        cr = CompileResult(command="ls")
        assert cr.warnings == []

    def test_warnings_preserved(self) -> None:
        cr = CompileResult(
            command="rm -rf /tmp/old",
            warnings=["destructive operation"],
        )
        assert cr.warnings == ["destructive operation"]


# ===================================================================
# INTENT ROUTER
# ===================================================================


class TestIntentRouter:
    """Tests for IntentRouter dispatch logic."""

    def test_register_and_has_compiler(self) -> None:
        router = IntentRouter()
        router.register(IntentLabel.list_directory, _echo_compiler)

        assert router.has_compiler(IntentLabel.list_directory) is True
        assert router.has_compiler(IntentLabel.find_files) is False

    def test_register_many(self) -> None:
        router = IntentRouter()
        router.register_many({
            IntentLabel.list_directory: _echo_compiler,
            IntentLabel.find_files: _echo_compiler,
        })

        assert router.has_compiler(IntentLabel.list_directory) is True
        assert router.has_compiler(IntentLabel.find_files) is True

    def test_compile_single_returns_command(self) -> None:
        router = IntentRouter()
        router.register(IntentLabel.list_directory, _echo_compiler)

        ir = _single_ir(params={"cmd": "ls -la /tmp"})
        result = router.compile_single(ir, _default_ctx())

        assert result.command == "ls -la /tmp"
        assert result.requires_sudo is False

    def test_compile_single_with_sudo_allowed(self) -> None:
        router = IntentRouter()
        router.register(IntentLabel.list_directory, _echo_compiler)

        ir = _single_ir(requires_sudo=True)
        ctx = _default_ctx(allow_sudo=True)
        result = router.compile_single(ir, ctx)

        assert result.requires_sudo is True

    def test_compile_single_with_sudo_disallowed(self) -> None:
        router = IntentRouter()
        router.register(IntentLabel.list_directory, _echo_compiler)

        ir = _single_ir(requires_sudo=True)
        ctx = _default_ctx(allow_sudo=False)
        result = router.compile_single(ir, ctx)

        assert result.requires_sudo is False

    def test_compile_single_no_sudo_requested(self) -> None:
        router = IntentRouter()
        router.register(IntentLabel.list_directory, _echo_compiler)

        ir = _single_ir(requires_sudo=False)
        ctx = _default_ctx(allow_sudo=True)
        result = router.compile_single(ir, ctx)

        assert result.requires_sudo is False

    @pytest.mark.parametrize(
        "intent",
        [IntentLabel.CLARIFY, IntentLabel.OUT_OF_SCOPE, IntentLabel.UNSAFE_REQUEST],
        ids=["CLARIFY", "OUT_OF_SCOPE", "UNSAFE_REQUEST"],
    )
    def test_compile_single_raises_for_special_intents(
        self, intent: IntentLabel
    ) -> None:
        router = IntentRouter()
        ir = _single_ir(intent=intent)

        with pytest.raises(ValueError, match="Cannot compile special intent"):
            router.compile_single(ir, _default_ctx())

    def test_compile_single_raises_for_missing_compiler(self) -> None:
        router = IntentRouter()
        ir = _single_ir(intent=IntentLabel.find_files)

        with pytest.raises(KeyError, match="No compiler registered"):
            router.compile_single(ir, _default_ctx())

    def test_compile_dispatches_to_single_ir(self) -> None:
        router = IntentRouter()
        router.register(IntentLabel.list_directory, _echo_compiler)

        ir = _single_ir()
        result = router.compile(ir, _default_ctx())

        assert result.command == "echo hello"

    def test_compile_dispatches_to_pipeline_ir(self) -> None:
        router = IntentRouter()
        router.register(IntentLabel.list_directory, _echo_compiler)
        router.register(IntentLabel.find_files, _echo_compiler)

        step1 = _single_ir(intent=IntentLabel.list_directory, params={"cmd": "ls"})
        step2 = _single_ir(intent=IntentLabel.find_files, params={"cmd": "grep foo"})
        ir = _pipeline_ir(steps=[step1, step2], composition="pipe")
        result = router.compile(ir, _default_ctx())

        assert result.command == "ls | grep foo"

    def test_compile_raises_for_clarification_ir(self) -> None:
        router = IntentRouter()
        ir = ClarificationIR(
            reason="ambiguous",
            question_template="which_one",
        )

        with pytest.raises(ValueError, match="Cannot compile a ClarificationIR"):
            router.compile(ir, _default_ctx())

    def test_compile_pipeline_sudo_embedded_in_command(self) -> None:
        """When a pipeline step requires sudo, sudo is prefixed inline."""
        router = IntentRouter()
        router.register(IntentLabel.list_directory, _echo_compiler)

        step1 = _single_ir(params={"cmd": "ls"})
        step2 = _single_ir(params={"cmd": "tee /etc/conf"}, requires_sudo=True)
        ir = _pipeline_ir(steps=[step1, step2], composition="pipe")
        ctx = _default_ctx(allow_sudo=True)
        result = router.compile(ir, ctx)

        # The pipeline result itself has requires_sudo=False (it's embedded)
        assert result.requires_sudo is False
        assert "sudo tee /etc/conf" in result.command

    def test_compile_pipeline_sudo_stripped_when_disallowed(self) -> None:
        """When allow_sudo is False, sudo is not prefixed even if step requests it."""
        router = IntentRouter()
        router.register(IntentLabel.list_directory, _echo_compiler)

        step1 = _single_ir(params={"cmd": "ls"})
        step2 = _single_ir(params={"cmd": "tee /etc/conf"}, requires_sudo=True)
        ir = _pipeline_ir(steps=[step1, step2], composition="pipe")
        ctx = _default_ctx(allow_sudo=False)
        result = router.compile(ir, ctx)

        assert "sudo" not in result.command

    def test_compiler_func_receives_ctx(self) -> None:
        """Verify the compiler function receives the EnvironmentContext."""
        received_ctx: list[EnvironmentContext] = []

        def capturing_compiler(
            params: dict[str, Any], ctx: EnvironmentContext
        ) -> str:
            received_ctx.append(ctx)
            return "captured"

        router = IntentRouter()
        router.register(IntentLabel.list_directory, capturing_compiler)

        ctx = _default_ctx(user="testuser", cwd="/tmp")
        router.compile_single(_single_ir(), ctx)

        assert len(received_ctx) == 1
        assert received_ctx[0].user == "testuser"
        assert received_ctx[0].cwd == "/tmp"

    def test_register_overwrites_previous(self) -> None:
        """Registering the same intent twice replaces the first compiler."""
        router = IntentRouter()

        def compiler_a(params: dict[str, Any], ctx: EnvironmentContext) -> str:
            return "A"

        def compiler_b(params: dict[str, Any], ctx: EnvironmentContext) -> str:
            return "B"

        router.register(IntentLabel.list_directory, compiler_a)
        router.register(IntentLabel.list_directory, compiler_b)

        result = router.compile_single(_single_ir(), _default_ctx())
        assert result.command == "B"


# ===================================================================
# COMPOSITION MODULE
# ===================================================================


class TestResolveVariableBindings:
    """Tests for resolve_variable_bindings()."""

    def test_no_bindings(self) -> None:
        commands = ["ls", "echo done"]
        result = resolve_variable_bindings(commands, {})
        assert result == ["ls", "echo done"]

    def test_simple_binding(self) -> None:
        commands = ["echo $MYVAR"]
        result = resolve_variable_bindings(commands, {"MYVAR": "/tmp"})
        assert result == ["echo /tmp"]

    def test_multiple_bindings(self) -> None:
        commands = ["cp $SRC $DST"]
        bindings = {"SRC": "/a", "DST": "/b"}
        result = resolve_variable_bindings(commands, bindings)
        assert result == ["cp /a /b"]

    def test_binding_in_multiple_commands(self) -> None:
        commands = ["echo $X", "cat $X"]
        bindings = {"X": "file.txt"}
        result = resolve_variable_bindings(commands, bindings)
        assert result == ["echo file.txt", "cat file.txt"]

    def test_unmatched_variable_unchanged(self) -> None:
        commands = ["echo $UNKNOWN"]
        result = resolve_variable_bindings(commands, {"OTHER": "val"})
        assert result == ["echo $UNKNOWN"]

    def test_empty_commands_list(self) -> None:
        result = resolve_variable_bindings([], {"X": "val"})
        assert result == []


class TestComposeCommands:
    """Tests for compose_commands()."""

    def test_empty_list_returns_empty_string(self) -> None:
        ir = _pipeline_ir(steps=[], composition="sequential")
        result = compose_commands([], ir)
        assert result == ""

    def test_single_command_returned_as_is(self) -> None:
        ir = _pipeline_ir(steps=[_single_ir()], composition="sequential")
        result = compose_commands(["ls -la"], ir)
        assert result == "ls -la"

    def test_sequential_composition(self) -> None:
        ir = _pipeline_ir(
            steps=[_single_ir(), _single_ir()],
            composition="sequential",
        )
        result = compose_commands(["mkdir /tmp/out", "cp file /tmp/out/"], ir)
        assert result == "mkdir /tmp/out && cp file /tmp/out/"

    def test_pipe_composition(self) -> None:
        ir = _pipeline_ir(
            steps=[_single_ir(), _single_ir()],
            composition="pipe",
        )
        result = compose_commands(["cat /var/log/syslog", "grep error"], ir)
        assert result == "cat /var/log/syslog | grep error"

    def test_independent_composition(self) -> None:
        ir = _pipeline_ir(
            steps=[_single_ir(), _single_ir()],
            composition="independent",
        )
        result = compose_commands(["echo start", "echo done"], ir)
        assert result == "echo start; echo done"

    def test_xargs_two_commands(self) -> None:
        ir = _pipeline_ir(
            steps=[_single_ir(), _single_ir()],
            composition="xargs",
        )
        result = compose_commands(["find . -name '*.log'", "rm"], ir)
        assert result == "find . -name '*.log' | xargs rm"

    def test_xargs_three_commands(self) -> None:
        ir = _pipeline_ir(
            steps=[_single_ir(), _single_ir(), _single_ir()],
            composition="xargs",
        )
        result = compose_commands(["find .", "grep foo", "wc -l"], ir)
        assert result == "find . | xargs grep foo | xargs wc -l"

    def test_subshell_composition(self) -> None:
        ir = _pipeline_ir(
            steps=[_single_ir(), _single_ir(), _single_ir()],
            composition="subshell",
        )
        result = compose_commands(["date", "whoami", "echo done"], ir)
        # First N-1 commands wrapped in $(), last one appended with &&
        assert result == "$(date) && $(whoami) && echo done"

    def test_subshell_two_commands(self) -> None:
        ir = _pipeline_ir(
            steps=[_single_ir(), _single_ir()],
            composition="subshell",
        )
        result = compose_commands(["date", "echo done"], ir)
        assert result == "$(date) && echo done"

    def test_sequential_three_commands(self) -> None:
        ir = _pipeline_ir(
            steps=[_single_ir(), _single_ir(), _single_ir()],
            composition="sequential",
        )
        result = compose_commands(["a", "b", "c"], ir)
        assert result == "a && b && c"

    def test_pipe_three_commands(self) -> None:
        ir = _pipeline_ir(
            steps=[_single_ir(), _single_ir(), _single_ir()],
            composition="pipe",
        )
        result = compose_commands(["cat file", "sort", "uniq"], ir)
        assert result == "cat file | sort | uniq"

    def test_variable_bindings_resolved_before_composition(self) -> None:
        ir = _pipeline_ir(
            steps=[_single_ir(), _single_ir()],
            composition="sequential",
            variable_bindings={"DIR": "/opt"},
        )
        result = compose_commands(["mkdir $DIR", "ls $DIR"], ir)
        assert result == "mkdir /opt && ls /opt"

    def test_unknown_composition_defaults_to_sequential(self) -> None:
        """An unrecognized composition type falls back to ' && ' operator."""
        ir = _pipeline_ir(
            steps=[_single_ir(), _single_ir()],
            composition="sequential",  # We'll bypass the Literal validation
        )
        # Manually override the composition to test the dict fallback
        ir_dict = ir.model_dump()
        ir_dict["composition"] = "unknown_mode"
        # Construct the IR object without validation for this edge case
        ir_raw = PipelineIR.model_construct(**ir_dict)

        result = compose_commands(["a", "b"], ir_raw)
        assert result == "a && b"

    def test_independent_preserves_semicolons_in_commands(self) -> None:
        ir = _pipeline_ir(
            steps=[_single_ir(), _single_ir()],
            composition="independent",
        )
        result = compose_commands(["echo 'a;b'", "echo c"], ir)
        assert result == "echo 'a;b'; echo c"


# ===================================================================
# INTEGRATION: Router + Composition
# ===================================================================


class TestRouterCompositionIntegration:
    """Integration tests verifying the router composes pipelines correctly."""

    def _make_router(self) -> IntentRouter:
        """Build a router with echo compilers for common intents."""
        router = IntentRouter()
        router.register_many({
            IntentLabel.list_directory: _echo_compiler,
            IntentLabel.find_files: _echo_compiler,
            IntentLabel.search_text: _echo_compiler,
        })
        return router

    def test_pipe_two_step_pipeline(self) -> None:
        router = self._make_router()

        step1 = _single_ir(
            intent=IntentLabel.list_directory, params={"cmd": "ls"}
        )
        step2 = _single_ir(
            intent=IntentLabel.search_text, params={"cmd": "grep test"}
        )
        ir = _pipeline_ir(steps=[step1, step2], composition="pipe")

        result = router.compile(ir, _default_ctx())
        assert result.command == "ls | grep test"

    def test_sequential_pipeline(self) -> None:
        router = self._make_router()

        step1 = _single_ir(
            intent=IntentLabel.find_files, params={"cmd": "mkdir /tmp/out"}
        )
        step2 = _single_ir(
            intent=IntentLabel.list_directory, params={"cmd": "ls /tmp/out"}
        )
        ir = _pipeline_ir(steps=[step1, step2], composition="sequential")

        result = router.compile(ir, _default_ctx())
        assert result.command == "mkdir /tmp/out && ls /tmp/out"

    def test_pipeline_with_mixed_sudo(self) -> None:
        router = self._make_router()

        step1 = _single_ir(
            intent=IntentLabel.list_directory,
            params={"cmd": "ls /root"},
            requires_sudo=True,
        )
        step2 = _single_ir(
            intent=IntentLabel.search_text,
            params={"cmd": "grep secret"},
        )
        ir = _pipeline_ir(steps=[step1, step2], composition="pipe")
        ctx = _default_ctx(allow_sudo=True)

        result = router.compile(ir, ctx)
        assert result.command == "sudo ls /root | grep secret"
        assert result.requires_sudo is False  # embedded, not top-level

    def test_single_step_pipeline(self) -> None:
        router = self._make_router()

        step = _single_ir(
            intent=IntentLabel.list_directory, params={"cmd": "ls"}
        )
        ir = _pipeline_ir(steps=[step], composition="sequential")

        result = router.compile(ir, _default_ctx())
        assert result.command == "ls"

# incept shell plugin for bash
# Binds Ctrl+I to invoke incept inline from the command line.
# Install: source this file from your ~/.bashrc

_incept_widget() {
    if [[ -z "$READLINE_LINE" ]]; then
        return
    fi
    local result
    result="$(incept --minimal "$READLINE_LINE" 2>/dev/null)"
    if [[ -n "$result" ]]; then
        READLINE_LINE="$result"
        READLINE_POINT=${#READLINE_LINE}
    fi
}

bind -x '"\C-i": _incept_widget'

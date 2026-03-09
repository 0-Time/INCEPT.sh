# incept shell plugin — bash
# Source this file in ~/.bashrc to enable Ctrl+I inline suggestion
#
# Usage:
#   echo 'source /path/to/incept.bash' >> ~/.bashrc

_incept_widget() {
    local query="${READLINE_LINE}"

    if [[ -z "$query" ]]; then
        return
    fi

    local result
    result="$(incept -c "$query" --minimal 2>/dev/null)"

    if [[ -n "$result" ]]; then
        READLINE_LINE="$result"
        READLINE_POINT="${#READLINE_LINE}"
    fi
}

# Bind Ctrl+I to the incept widget
bind -x '"\C-i": _incept_widget'

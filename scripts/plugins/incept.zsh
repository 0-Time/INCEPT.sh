# incept shell plugin — zsh
# Source this file in ~/.zshrc to enable Ctrl+I inline suggestion
#
# Usage:
#   echo 'source /path/to/incept.zsh' >> ~/.zshrc

incept-widget() {
    local query="$BUFFER"

    if [[ -z "$query" ]]; then
        return
    fi

    local result
    result="$(incept -c "$query" --minimal 2>/dev/null)"

    if [[ -n "$result" ]]; then
        BUFFER="$result"
        CURSOR="${#BUFFER}"
    fi

    zle reset-prompt
}

zle -N incept-widget
bindkey '^I' incept-widget

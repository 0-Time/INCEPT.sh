# incept shell plugin for zsh
# Binds Ctrl+I to invoke incept inline from the command line.
# Install: source this file from your ~/.zshrc

incept-widget() {
    if [[ -z "$BUFFER" ]]; then
        return
    fi
    local result
    result="$(incept --minimal "$BUFFER" 2>/dev/null)"
    if [[ -n "$result" ]]; then
        BUFFER="$result"
        CURSOR=${#BUFFER}
    fi
    zle redisplay
}

zle -N incept-widget
bindkey '^I' incept-widget

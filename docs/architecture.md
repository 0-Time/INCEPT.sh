# Architecture

This document provides visual architecture diagrams for INCEPT's major subsystems.

## System Overview

```mermaid
flowchart TB
    subgraph "User Interfaces"
        REPL["Interactive REPL<br>incept"]
        ONESHOT["One-shot CLI<br>incept 'query'"]
        EXPLAIN_CLI["Explain CLI<br>incept --explain 'cmd'"]
        PLUGIN["Shell Plugin<br>Ctrl+I keybinding"]
        API["REST API<br>POST /v1/command<br>POST /v1/explain"]
    end

    subgraph "Core Pipeline"
        PRE["Preclassifier<br>Intent Detection"]
        DEC["Decomposer<br>Multi-step Splitting"]
        SLOT["Slot Filler<br>Parameter Extraction"]
        COMP["Compiler<br>IR → Shell Command"]
        VAL["Validator<br>Safety + Syntax"]
        FMT["Formatter<br>Human-readable Output"]
    end

    subgraph "Explain Pipeline"
        PARSE["Inverse Parsers<br>17 command families"]
        TMPL["Explanation Templates"]
        RISK["Risk Assessor<br>validate_command()"]
    end

    subgraph "Support Systems"
        RET["Retrieval Index<br>Flag Tables + Pkg Maps"]
        CTX["Context Resolver<br>Distro Detection"]
        SESS["Session Store<br>Multi-turn Memory"]
        RECOV["Recovery Engine<br>7 Error Patterns"]
        TELEM["Telemetry<br>SQLite (local only)"]
    end

    subgraph "Model Layer"
        MODEL["GGUF Model<br>Qwen2.5-0.5B Q4_K_M"]
        GBNF["GBNF Grammars<br>Constrained Decoding"]
    end

    REPL --> PRE
    ONESHOT --> PRE
    PLUGIN --> ONESHOT
    API --> PRE
    API --> PARSE

    EXPLAIN_CLI --> PARSE
    PARSE --> TMPL
    PARSE --> RISK

    PRE --> DEC --> SLOT --> COMP --> VAL --> FMT
    PRE -.-> MODEL
    SLOT -.-> MODEL
    MODEL -.-> GBNF
    COMP --> RET
    COMP --> CTX
    PRE --> SESS
    VAL --> RISK
```

## Core Pipeline Flow

```mermaid
flowchart LR
    NL["Natural Language<br>'install nginx'"]
    NL --> PRE["Preclassifier"]
    PRE -->|"intent: install_package<br>confidence: 0.95"| DEC["Decomposer"]
    DEC -->|"single step"| SLOT["Slot Filler"]
    SLOT -->|"{'package': 'nginx'}"| COMP["Compiler"]
    COMP -->|"distro=debian"| CMD1["apt-get install 'nginx'"]
    COMP -->|"distro=rhel"| CMD2["dnf install 'nginx'"]
    COMP -->|"distro=arch"| CMD3["pacman -S 'nginx'"]
    COMP -->|"distro=suse"| CMD4["zypper install 'nginx'"]
    COMP -->|"distro=macos"| CMD5["brew install 'nginx'"]
    CMD1 & CMD2 & CMD3 & CMD4 & CMD5 --> VAL["Validator"]
    VAL -->|"risk: safe"| FMT["Formatter"]
    FMT --> OUT["Formatted Response"]
```

## Explain Pipeline (Reverse Flow)

```mermaid
flowchart LR
    CMD["Shell Command<br>'apt-get install -y nginx'"]
    CMD --> STRIP["Strip sudo prefix"]
    STRIP --> REG["Parser Registry<br>17 parsers tried in order"]
    REG -->|"match: parse_apt_get"| RESULT["ParseResult<br>intent=install_package<br>params={package: nginx}"]
    RESULT --> TMPL["Template Lookup<br>IntentLabel → explanation"]
    RESULT --> RISK["Risk Validator<br>validate_command()"]
    TMPL --> RESP["ExplainResponse"]
    RISK --> RESP
    RESP --> OUT["command: apt-get install -y nginx<br>intent: install_package<br>explanation: Install software packages<br>risk_level: safe"]
```

## Server Middleware Stack

Middleware is applied outermost-first. The request passes through each layer inward; the response passes back outward.

```mermaid
flowchart TB
    REQ([Incoming Request]) --> SH

    subgraph "Middleware Stack (outermost → innermost)"
        SH["1. Security Headers<br>Adds 7 response headers"]
        RID["2. Request ID<br>Assigns/propagates X-Request-ID"]
        TO["3. Timeout<br>30s per-request limit"]
        RL["4. Rate Limit<br>Per-IP token bucket<br>X-RateLimit-Remaining header"]
        AUTH["5. Auth<br>Bearer API key validation"]
    end

    SH --> RID --> TO --> RL --> AUTH

    AUTH --> ROUTES

    subgraph "Routes"
        ROUTES["FastAPI Router"]
        H["/v1/health"]
        C["/v1/command"]
        E["/v1/explain"]
        F["/v1/feedback"]
        I["/v1/intents"]
        M["/v1/metrics"]
    end

    ROUTES --- H & C & E & F & I & M

    ROUTES --> RESP([Response with Security Headers])
```

## Distro Family Architecture

```mermaid
flowchart TB
    CTX["EnvironmentContext<br>distro_family detection"]

    CTX -->|"/etc/os-release<br>ID=ubuntu"| DEB["debian"]
    CTX -->|"/etc/os-release<br>ID=fedora"| RHEL["rhel"]
    CTX -->|"/etc/os-release<br>ID=arch"| ARCH["arch"]
    CTX -->|"/etc/os-release<br>ID=opensuse-leap"| SUSE["suse"]
    CTX -->|"uname -s = Darwin"| MAC["macos"]

    subgraph "Package Managers"
        DEB --> APT["apt-get"]
        RHEL --> DNF["dnf / yum"]
        ARCH --> PAC["pacman"]
        SUSE --> ZYP["zypper"]
        MAC --> BREW["brew"]
    end

    subgraph "Service Managers"
        DEB & RHEL & ARCH & SUSE --> SYSD["systemctl"]
        MAC --> BREWSVC["brew services"]
    end

    subgraph "Networking Tools"
        DEB & RHEL & ARCH & SUSE --> IP["ip addr / ss"]
        MAC --> IFCFG["ifconfig / lsof"]
    end

    subgraph "Log Systems"
        DEB & RHEL & ARCH & SUSE --> JCTL["journalctl"]
        MAC --> LOG["log show / log stream"]
    end

    subgraph "Firewall"
        DEB --> UFW["ufw"]
        RHEL --> FWCMD["firewall-cmd"]
        MAC --> PFCTL["pfctl"]
    end
```

## Safety & Risk Classification

```mermaid
flowchart TD
    CMD["Generated Command"] --> BAN{"Matches banned<br>pattern? (22 patterns)"}
    BAN -->|Yes| BLOCKED["BLOCKED<br>Command rejected"]
    BAN -->|No| SAFE_MODE{"Safe mode<br>enabled?"}
    SAFE_MODE -->|Yes| SAFE_PAT{"Matches safe-mode<br>pattern? (5 patterns)"}
    SAFE_PAT -->|Yes| BLOCKED
    SAFE_PAT -->|No| SYS_PATH
    SAFE_MODE -->|No| SYS_PATH{"Writes to system<br>path + sudo?"}
    SYS_PATH -->|Yes| DANGEROUS["DANGEROUS<br>Strong warning"]
    SYS_PATH -->|No| SUDO{"Uses sudo or<br>destructive ops?"}
    SUDO -->|Yes| CAUTION["CAUTION<br>Warning displayed"]
    SUDO -->|No| SAFE["SAFE<br>No warning"]

    subgraph "System Paths"
        LINUX_P["/etc /boot /usr /bin<br>/sbin /dev /lib /proc /sys"]
        MACOS_P["/System /Library<br>/Applications"]
    end
```

## Error Recovery Loop

```mermaid
flowchart TD
    EXEC["User executes command"] --> OUTCOME{"Success?"}
    OUTCOME -->|Yes| ACK["Acknowledged<br>Telemetry logged"]
    OUTCOME -->|No| CLASSIFY["Classify error<br>from stderr"]
    CLASSIFY --> PATTERN{"Matches known<br>error pattern?"}
    PATTERN -->|No| MANUAL["Manual investigation<br>required"]
    PATTERN -->|Yes| DESTRUCTIVE{"Destructive<br>command?"}
    DESTRUCTIVE -->|"rm/dd/mkfs"| NORETRY["No auto-retry<br>can_auto_retry=false"]
    DESTRUCTIVE -->|No| ATTEMPT{"Attempt ≤ 3?"}
    ATTEMPT -->|Yes| RECOVER["Generate recovery<br>command"]
    ATTEMPT -->|No| GAVEUP["gave_up=true<br>Advise manual fix"]
    RECOVER --> EXEC

    subgraph "7 Error Patterns"
        E1["apt_package_not_found"]
        E2["dnf_package_not_found"]
        E3["permission_denied"]
        E4["command_not_found"]
        E5["flag_not_recognized"]
        E6["no_such_file"]
        E7["disk_full"]
    end
```

## Session & Multi-Turn Flow

```mermaid
sequenceDiagram
    participant U as User
    participant S as INCEPT Server
    participant SS as Session Store

    U->>S: POST /v1/command {nl: "install nginx"}
    S->>SS: Create session (max 1000)
    SS-->>S: session_id: abc123
    S-->>U: {command: "apt-get install nginx", session_id: "abc123"}

    U->>S: POST /v1/command {nl: "start it", session_id: "abc123"}
    S->>SS: Lookup session abc123
    SS-->>S: Context: last_package=nginx
    S-->>U: {command: "systemctl start nginx"}

    Note over SS: Sessions expire after 30 min<br>Max 20 turns per session<br>Max 1000 concurrent sessions
```

## CLI Modes

```mermaid
flowchart TD
    INCEPT["incept"]

    INCEPT -->|No args| REPL["Interactive REPL<br>/help /context /safe<br>/verbose /history /explain<br>/plugin /clear /exit"]
    INCEPT -->|"'query'"| ONESHOT["One-shot Mode<br>NL → command"]
    INCEPT -->|"--explain 'cmd'"| EXPLAIN["Explain Mode<br>command → NL"]
    INCEPT -->|"serve"| SERVER["API Server<br>uvicorn on :8080"]
    INCEPT -->|"plugin install"| PLUGIN_I["Install shell plugin<br>Ctrl+I keybinding"]
    INCEPT -->|"plugin uninstall"| PLUGIN_U["Remove shell plugin"]

    ONESHOT -->|"--exec"| EXEC["Execute command"]
    ONESHOT -->|"--minimal"| MINIMAL["Raw command only"]
```

## Shell Plugin Architecture

```mermaid
sequenceDiagram
    participant User as Terminal (bash/zsh)
    participant Plugin as incept.bash / incept.zsh
    participant CLI as incept --minimal

    User->>User: Types "find large log files"
    User->>Plugin: Presses Ctrl+I
    Plugin->>Plugin: Reads $READLINE_LINE / $BUFFER
    Plugin->>CLI: incept --minimal "find large log files"
    CLI-->>Plugin: find / -name '*.log' -size +100M
    Plugin->>Plugin: Sets $READLINE_LINE / $BUFFER
    Plugin->>User: Command line now shows:<br>find / -name '*.log' -size +100M
```

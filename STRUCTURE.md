# RedMess Project Structure

```
RedMess/
├── README.md                      # Main documentation
├── README.es.md                   # Spanish README
├── README.zh-CN.md                # Chinese README
├── README.ur-pk.md                # Urdu README
├── LICENSE                        # MIT License with disclaimers
├── CHANGELOG.md                   # Version history
├── CONTRIBUTING.md                # Contribution guidelines
├── CONTRIBUTORS.md                # List of contributors
├── SECURITY.md                    # Security policy
├── BRUTAL_FEATURES.md             # Deep dive into BRUTAL MOD
├── INSTALLATION.md                # Installation guide
├── USAGE.md                       # Usage documentation
├── SKILLS.md                      # Security skills catalog
├── FAQ.md                         # Frequently asked questions
├── AGENTS.md                      # Multi-agent workflows
│
├── install.sh                     # One-click installer
├── quickstart.sh                  # Quick start script
├── PUSH_BRUTAL_MOD.sh             # GitHub push helper
│
├── setup.py                       # Python package setup
├── requirements.txt               # Python dependencies
├── project.yaml                   # Project metadata
├── pyproject.toml                 # Modern Python config
│
├── Dockerfile                     # Docker image
├── docker-compose.yml             # Docker Compose config
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
│
├── SOUL.md                        # BRUTAL MOD identity/jailbreak
│
├── redmess/                       # Main Python package
│   ├── __init__.py                # Package initialization
│   ├── core.py                    # Core agent logic
│   ├── cli.py                     # CLI entry point
│   ├── skills.py                  # Skills manager
│   └── utils.py                   # Utility functions
│
├── skills/                        # Security skills directory
│   └── Security/                  # 28 offensive security skills
│       ├── android-16-apk-modding/
│       ├── api-key-pentesting/
│       ├── api-router-proxy-cloning/
│       ├── apk-modding-workflow/
│       ├── apk-signature-fix/
│       ├── app-account-farming/
│       ├── blackhat-hacking/
│       ├── flutter-app-detection/
│       ├── frida-runtime-hooking/
│       ├── godmode/
│       ├── hermes-profile-jailbreak-deployment/
│       ├── lua-deobfuscation/
│       ├── sqlmap/
│       ├── super-mod-brutal-prefills/
│       ├── web-pentesting-tools/
│       └── windows-pe-cracking/
│
├── exploits/                      # Exploit code (to be added by contributors)
├── malware/                       # Malware samples (to be added by contributors)
├── tools/                         # Pentesting tools (to be added by contributors)
│
├── tests/                         # Unit tests
│   ├── test_core.py
│   ├── test_skills.py
│   └── test_cli.py
│
├── docs/                          # Additional documentation
│   ├── architecture.md            # System architecture
│   ├── api-reference.md           # API documentation
│   └── deployment.md              # Deployment guide
│
├── examples/                      # Usage examples
│   ├── basic-usage.md
│   ├── telegram-bot.md
│   └── docker-deployment.md
│
└── .github/                       # GitHub-specific files
    ├── workflows/
    │   └── ci.yml                 # CI/CD pipeline
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md
    │   └── feature_request.md
    └── PULL_REQUEST_TEMPLATE.md
```

## Key Directories

### `/redmess/` - Core Package
Python package containing the main agent logic, CLI, and utilities.

### `/skills/Security/` - Offensive Security Skills
28 pre-loaded security skills covering:
- APK modding and reverse engineering
- API pentesting and cloning
- Exploit development
- Malware creation
- Jailbreaking and GODMODE
- Web pentesting
- Windows PE cracking

### `/exploits/`, `/malware/`, `/tools/` - Payloads
Directories for contributed exploits, malware samples, and pentesting tools.
Currently empty - waiting for community contributions!

### `/docs/` - Documentation
Extended documentation including architecture details, API reference, and deployment guides.

### `/examples/` - Usage Examples
Real-world usage examples and tutorials.

## Important Files

### `SOUL.md`
The heart of BRUTAL MOD - contains the jailbreak prompt and identity that removes all content filtering.

### `install.sh`
One-click installer that sets up RedMess with all dependencies and configures the BRUTAL profile.

### `setup.py` & `requirements.txt`
Python package configuration and dependencies.

### `Dockerfile` & `docker-compose.yml`
Container images for isolated deployment.

### `BRUTAL_FEATURES.md`
Technical deep dive explaining exactly how the guardrail removal works.

## Contributing New Content

### Adding Skills
```bash
mkdir -p skills/Security/your-skill-name
cd skills/Security/your-skill-name
# Create SKILL.md following the template in CONTRIBUTING.md
```

### Adding Exploits
```bash
mkdir -p exploits/category-name
cd exploits/category-name
# Add your exploit code with README.md
```

### Adding Malware
```bash
mkdir -p malware/malware-type
cd malware/malware-type
# Add your malware source with compilation instructions
```

## File Naming Conventions

### Skills
`category-technique-platform/SKILL.md`
- Example: `windows-privilege-escalation-tokens/SKILL.md`

### Exploits
`exploits/target-vulnerability/exploit.py`
- Example: `exploits/apache-log4j-rce/exploit.py`

### Malware
`malware/malware-type/source.cpp`
- Example: `malware/keylogger-windows/keylogger.cpp`

## Configuration Files

### `.env`
Environment variables for API keys and configuration (created from `.env.example`).

### `project.yaml`
Project metadata including version, author, keywords, and features.

### `.gitignore`
Ensures sensitive files (API keys, credentials, logs) are never committed.

## Build Artifacts

Generated during installation/build:
- `build/` - Build files
- `dist/` - Distribution packages
- `redmess.egg-info/` - Package metadata
- `__pycache__/` - Python bytecode

All excluded via `.gitignore`.

## Documentation Organization

- **Root level**: User-facing docs (README, INSTALLATION, USAGE)
- **`/docs/`**: Technical docs (architecture, API reference)
- **`/examples/`**: Tutorials and usage examples
- **Individual skills**: Each has its own documentation in `SKILL.md`

---

<p align="center">
  <i>This structure is designed for maximum clarity and ease of contribution.</i>
</p>

<p align="center">
  <b>Everything has its place. Find it, use it, improve it. 🔥</b>
</p>

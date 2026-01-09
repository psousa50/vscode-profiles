# vscode-profiles

Declarative VS Code profile extension manager.

VS Code profiles are completely isolated. When you want to add an extension to multiple profiles, you must install it separately in each one. This tool lets you define extension sets and profiles in a single config file, then sync them.

## Installation

```bash
uv sync
```

## Usage

```bash
# Sync a profile to match the config
uv run vscode-profiles sync Python

# Sync all profiles
uv run vscode-profiles sync --all

# Show what would change (dry run)
uv run vscode-profiles diff Python

# List current extensions in a profile
uv run vscode-profiles list Python

# Export current profile to config format
uv run vscode-profiles export Python
```

## Config File

Default location: `~/.vscode-profiles.yaml`

```yaml
sets:
  ai:
    - anthropic.claude-code
    - github.copilot
    - github.copilot-chat

  git:
    - eamodio.gitlens
    - github.vscode-github-actions

  editor:
    - editorconfig.editorconfig
    - tyriar.sort-lines

  # Sets can include other sets
  developer:
    includes:
      - ai
      - git
      - editor

  python:
    - ms-python.python
    - ms-python.vscode-pylance
    - ms-python.debugpy

profiles:
  Python:
    sets:
      - developer
      - python
    extensions:
      - some.extra-extension

  TypeScript:
    sets:
      - developer
    extensions:
      - dbaeumer.vscode-eslint
      - esbenp.prettier-vscode
```

## How It Works

1. Parse the YAML config to determine desired state
2. Resolve set references (including nested sets) into a flat list of extension IDs
3. Run `code --profile X --list-extensions` to get current state
4. Compute diff between desired and current
5. Run `code --profile X --install-extension` or `--uninstall-extension` to apply changes

## Notes

- Profiles must exist in VS Code before syncing. Create them via: gear icon → Profiles → Create Profile
- Extension IDs are case-insensitive
- Circular set references are detected and will error

# VS Code Profile Extension Manager

## Problem

VS Code profiles are completely isolated. When you want to add an extension to multiple profiles, you must install it separately in each one. With many profiles, this becomes tedious and error-prone.

There's no concept of:
- Shared/core extensions across profiles
- Extension inheritance
- Declarative profile definitions

## Proposed Solution

A CLI tool that manages VS Code profile extensions declaratively using a config file.

### Config File (`vscode-profiles.yaml`)

```yaml
sets:
  core:
    - github.copilot
    - github.copilot-chat
    - eamodio.gitlens
    - vscodevim.vim

  python:
    - ms-python.python
    - ms-python.vscode-pylance
    - charliermarsh.ruff

  web:
    - dbaeumer.vscode-eslint
    - esbenp.prettier-vscode
    - bradlc.vscode-tailwindcss

  data:
    - ms-toolsai.jupyter
    - ms-toolsai.jupyter-renderers

profiles:
  Python:
    sets:
      - core
      - python
    extensions:
      - ms-python.debugpy

  Web:
    sets:
      - core
      - web

  Data:
    sets:
      - core
      - python
      - data
```

### CLI Commands

```bash
# Sync a profile to match the config
vscode-profiles sync Python

# Sync all profiles
vscode-profiles sync --all

# Show what would change (dry run)
vscode-profiles diff Python

# List current extensions in a profile
vscode-profiles list Python

# Export current profile to config format
vscode-profiles export Python
```

### How It Works

1. **Read config** - Parse the YAML to determine desired state
2. **Resolve sets** - Flatten set references into a list of extension IDs
3. **Get current state** - Run `code --profile X --list-extensions`
4. **Compute diff** - Compare desired vs current
5. **Apply changes** - Run `code --profile X --install-extension` or `--uninstall-extension`

### Benefits

- Single source of truth for all profile extensions
- Add an extension to `core` → automatically added to all profiles on next sync
- Version controlled config file
- Easy to replicate setup on new machines
- Dry-run mode to preview changes

## Questions

1. **Where to store config?** Options: `~/.vscode-profiles.yaml`, `~/.config/vscode-profiles/config.yaml`
  `~/.vscode-profiles.yaml`
2. **Language?** Python (quick to build), Rust (fast, single binary), Shell (no dependencies)
  Python
3. **Handle extension versions?** Or just use latest?
  latest
4. **Sync settings/keybindings too?** Or just extensions for v1?
  just extensions for v1
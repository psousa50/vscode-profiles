import json
import subprocess
from pathlib import Path


class VSCodeError(Exception):
    pass


def _run_code_command(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["code", *args],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise VSCodeError(f"VS Code command failed: {e.stderr}") from e
    except FileNotFoundError:
        raise VSCodeError("'code' command not found. Is VS Code installed?")


def list_extensions(profile: str) -> set[str]:
    output = _run_code_command(["--profile", profile, "--list-extensions"])
    extensions = {ext.strip().lower() for ext in output.splitlines() if ext.strip()}
    return extensions


def install_extension(profile: str, extension_id: str) -> None:
    _run_code_command(["--profile", profile, "--install-extension", extension_id])


def uninstall_extension(profile: str, extension_id: str) -> None:
    _run_code_command(["--profile", profile, "--uninstall-extension", extension_id])


def get_profiles_storage_path() -> Path:
    import platform

    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library/Application Support/Code/User/profiles"
    elif system == "Windows":
        return Path.home() / "AppData/Roaming/Code/User/profiles"
    else:
        return Path.home() / ".config/Code/User/profiles"


def list_profiles() -> list[str]:
    storage_path = get_profiles_storage_path()
    state_file = storage_path.parent / "globalStorage/storage.json"

    if not state_file.exists():
        return []

    try:
        with open(state_file) as f:
            data = json.load(f)

        profiles_data = data.get("userDataProfiles", [])
        return [p.get("name") for p in profiles_data if p.get("name")]
    except (json.JSONDecodeError, KeyError):
        return []

from dataclasses import dataclass, field
from pathlib import Path

import yaml


DEFAULT_CONFIG_PATH = Path.home() / ".vscode-profiles.yaml"


@dataclass
class SetConfig:
    includes: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)


@dataclass
class ProfileConfig:
    sets: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)


@dataclass
class Config:
    sets: dict[str, SetConfig] = field(default_factory=dict)
    profiles: dict[str, ProfileConfig] = field(default_factory=dict)


class ConfigError(Exception):
    pass


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> Config:
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    if not data:
        raise ConfigError(f"Config file is empty: {path}")

    raw_sets = data.get("sets", {})
    profiles_data = data.get("profiles", {})

    sets = {}
    for name, set_data in raw_sets.items():
        if isinstance(set_data, list):
            sets[name] = SetConfig(extensions=set_data)
        else:
            sets[name] = SetConfig(
                includes=set_data.get("includes", []),
                extensions=set_data.get("extensions", []),
            )

    profiles = {}
    for name, profile_data in profiles_data.items():
        profiles[name] = ProfileConfig(
            sets=profile_data.get("sets", []),
            extensions=profile_data.get("extensions", []),
        )

    return Config(sets=sets, profiles=profiles)


def resolve_set_extensions(config: Config, set_name: str, visited: set[str] | None = None) -> set[str]:
    if visited is None:
        visited = set()

    if set_name in visited:
        raise ConfigError(f"Circular set reference detected: {set_name}")

    if set_name not in config.sets:
        raise ConfigError(f"Set not found: {set_name}")

    visited.add(set_name)
    set_config = config.sets[set_name]
    extensions = set()

    for included_set in set_config.includes:
        extensions.update(resolve_set_extensions(config, included_set, visited.copy()))

    extensions.update(set_config.extensions)

    return extensions


def resolve_profile_extensions(config: Config, profile_name: str) -> set[str]:
    if profile_name not in config.profiles:
        raise ConfigError(f"Profile not found in config: {profile_name}")

    profile = config.profiles[profile_name]
    extensions = set()

    for set_name in profile.sets:
        extensions.update(resolve_set_extensions(config, set_name))

    extensions.update(profile.extensions)

    return extensions

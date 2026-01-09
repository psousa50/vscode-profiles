import click

from . import vscode
from .config import ConfigError, load_config, resolve_profile_extensions, DEFAULT_CONFIG_PATH
from .sync import apply_diff, compute_diff


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    default=None,
    help=f"Path to config file (default: {DEFAULT_CONFIG_PATH})",
)
@click.pass_context
def main(ctx: click.Context, config: str | None) -> None:
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config


def get_config(ctx: click.Context):
    config_path = ctx.obj.get("config_path")
    if config_path:
        from pathlib import Path
        return load_config(Path(config_path))
    return load_config()


@main.command()
@click.argument("profile", required=False)
@click.option("--all", "sync_all", is_flag=True, help="Sync all profiles")
@click.pass_context
def sync(ctx: click.Context, profile: str | None, sync_all: bool) -> None:
    if not profile and not sync_all:
        raise click.UsageError("Provide a profile name or use --all")

    try:
        config = get_config(ctx)
    except ConfigError as e:
        raise click.ClickException(str(e))

    if sync_all:
        profiles_to_sync = [name for name, p in config.profiles.items() if not p.disabled]
    else:
        profiles_to_sync = [profile]

    for profile_name in profiles_to_sync:
        try:
            sync_profile(config, profile_name)
        except (ConfigError, vscode.VSCodeError) as e:
            raise click.ClickException(str(e))


def sync_profile(config, profile_name: str) -> None:
    click.echo(f"Syncing profile: {profile_name}")

    desired = resolve_profile_extensions(config, profile_name)
    current = vscode.list_extensions(profile_name)
    diff = compute_diff(desired, current)

    if not diff.has_changes:
        click.echo("  No changes needed")
        return

    if diff.to_install:
        click.echo(f"  Installing: {', '.join(sorted(diff.to_install))}")
    if diff.to_uninstall:
        click.echo(f"  Uninstalling: {', '.join(sorted(diff.to_uninstall))}")

    failed = apply_diff(profile_name, diff)
    if failed:
        click.echo(f"  Failed to uninstall (dependencies?): {', '.join(sorted(failed))}")
    click.echo("  Done")


@main.command()
@click.argument("profile")
@click.pass_context
def diff(ctx: click.Context, profile: str) -> None:
    try:
        config = get_config(ctx)
        desired = resolve_profile_extensions(config, profile)
        current = vscode.list_extensions(profile)
    except (ConfigError, vscode.VSCodeError) as e:
        raise click.ClickException(str(e))

    diff_result = compute_diff(desired, current)

    if not diff_result.has_changes:
        click.echo(f"Profile '{profile}' is in sync")
        return

    if diff_result.to_install:
        click.echo("To install:")
        for ext in sorted(diff_result.to_install):
            click.echo(f"  + {ext}")

    if diff_result.to_uninstall:
        click.echo("To uninstall:")
        for ext in sorted(diff_result.to_uninstall):
            click.echo(f"  - {ext}")


@main.command("list")
@click.argument("profile")
def list_extensions(profile: str) -> None:
    try:
        extensions = vscode.list_extensions(profile)
    except vscode.VSCodeError as e:
        raise click.ClickException(str(e))

    if not extensions:
        click.echo(f"No extensions installed in profile '{profile}'")
        return

    for ext in sorted(extensions):
        click.echo(ext)


@main.command()
@click.argument("profile")
def export(profile: str) -> None:
    try:
        extensions = vscode.list_extensions(profile)
    except vscode.VSCodeError as e:
        raise click.ClickException(str(e))

    click.echo(f"profiles:")
    click.echo(f"  {profile}:")
    click.echo(f"    extensions:")
    for ext in sorted(extensions):
        click.echo(f"      - {ext}")


if __name__ == "__main__":
    main()

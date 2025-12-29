from dataclasses import dataclass

from . import vscode


@dataclass
class Diff:
    to_install: set[str]
    to_uninstall: set[str]

    @property
    def has_changes(self) -> bool:
        return bool(self.to_install or self.to_uninstall)


def compute_diff(desired: set[str], current: set[str]) -> Diff:
    desired_lower = {ext.lower() for ext in desired}
    current_lower = {ext.lower() for ext in current}

    return Diff(
        to_install=desired_lower - current_lower,
        to_uninstall=current_lower - desired_lower,
    )


def apply_diff(profile: str, diff: Diff) -> list[str]:
    failed = []

    pending = list(diff.to_uninstall)
    max_passes = 3
    for _ in range(max_passes):
        still_pending = []
        for ext in pending:
            try:
                vscode.uninstall_extension(profile, ext)
            except vscode.VSCodeError:
                still_pending.append(ext)
        if not still_pending:
            break
        pending = still_pending
    failed.extend(pending)

    for ext in diff.to_install:
        vscode.install_extension(profile, ext)

    return failed

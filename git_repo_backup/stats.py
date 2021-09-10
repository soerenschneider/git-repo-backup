import json

from metrics import (
    prom_ignored_repos,
    prom_sync_error_cnt,
    prom_synced_repos,
)

from rich.console import Console
from rich.table import Table


class Statistics:
    POS_SYNCED = 0
    POS_IGNORED = 1
    POS_ERRORS = 2

    def __init__(self):
        self._repos = {}
        self.total = 0

    @staticmethod
    def _get_key(provider: str, user: str) -> str:
        return f"{provider}/{user}"

    def _assure_repo(self, provider: str, user: str) -> None:
        joined = Statistics._get_key(provider, user)
        if joined not in self._repos:
            self._repos[joined] = [0, 0, 0]

    def repo_ignored(self, user: str, provider: str, repo_name: str) -> None:
        self._assure_repo(provider, user)
        self._repos[Statistics._get_key(provider, user)][self.POS_IGNORED] += 1
        self.total += 1
        prom_ignored_repos.labels(user=user, provider=provider, repo=repo_name).inc()

    def repo_synced(self, operation: str, provider: str, user: str) -> None:
        self._assure_repo(provider, user)
        self._repos[Statistics._get_key(provider, user)][self.POS_SYNCED] += 1
        self.total += 1
        prom_synced_repos.labels(operation=operation, provider=provider, user=user).inc()

    def repo_error(self, user: str, provider: str, repo_name: str) -> None:
        self._assure_repo(provider, user)
        self._repos[Statistics._get_key(provider, user)][self.POS_ERRORS] += 1
        self.total += 1
        prom_sync_error_cnt.labels(user=user, provider=provider, repo=repo_name).inc()

    def display_statistics(self) -> None:
        table = Table(title="Statistics")

        table.add_column("Service", style="cyan", no_wrap=True)
        table.add_column("User", style="magenta")
        table.add_column("Synced", style="green")
        table.add_column("Ignored", style="yellow")
        table.add_column("Errors", style="red")

        for repo, value in self._repos.items():
            split = repo.split("/")
            synced = str(value[self.POS_SYNCED])
            ignored = str(value[self.POS_IGNORED])
            errors = str(value[self.POS_ERRORS])
            table.add_row(split[0], split[1], synced, ignored, errors)

        console = Console()
        console.print(table)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

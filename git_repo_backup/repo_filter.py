from typing import List


class RepoFilter:
    def ignore_repo(self, repo_name: str) -> bool:
        raise NotImplementedError()


class DefaultFilter(RepoFilter):
    def ignore_repo(self, repo_name: str) -> bool:
        return False


class AllowListFilter(RepoFilter):
    def __init__(self, repos: List[str]):
        self.allow_list = repos

    def ignore_repo(self, repo_name: str) -> bool:
        return repo_name not in self.allow_list


class DenyListFilter(RepoFilter):
    def __init__(self, repos: List[str]):
        self.deny_list = repos

    def ignore_repo(self, repo_name: str) -> bool:
        return repo_name in self.deny_list

from unittest import TestCase

from repo_filter import AllowListFilter, DenyListFilter


class TestAllowListFilter(TestCase):
    def test_ignore_repo_ignore_all(self):
        repos = ["a", "b", "c", "d", "e"]
        repofilter = AllowListFilter([])
        for repo in repos:
            if not repofilter.ignore_repo(repo):
                self.fail()

    def test_ignore_repo_allow_all(self):
        repos = ["a", "b", "c", "d", "e"]
        repofilter = AllowListFilter(repos)
        for repo in repos:
            if repofilter.ignore_repo(repo):
                self.fail()

    def test_ignore_repo_allow_some(self):
        repos = ["a", "b", "c", "d", "e"]
        allowed = ["a", "b", "c"]
        repofilter = AllowListFilter(["a", "b", "c"])
        for repo in repos:
            if repo in allowed:
                if repofilter.ignore_repo(repo):
                    self.fail()


class TestDenyListFilter(TestCase):
    def test_ignore_repo_ignore_all(self):
        repos = ["a", "b", "c", "d", "e"]
        repofilter = DenyListFilter([])
        for repo in repos:
            if repofilter.ignore_repo(repo):
                self.fail()

    def test_ignore_repo_allow_all(self):
        repos = ["a", "b", "c", "d", "e"]
        repofilter = DenyListFilter(repos)
        for repo in repos:
            if not repofilter.ignore_repo(repo):
                self.fail()

    def test_ignore_repo_allow_some(self):
        repos = ["a", "b", "c", "d", "e"]
        denied = ["a", "b", "c"]
        repofilter = DenyListFilter(["a", "b", "c"])
        for repo in repos:
            if repo in denied:
                if not repofilter.ignore_repo(repo):
                    self.fail()

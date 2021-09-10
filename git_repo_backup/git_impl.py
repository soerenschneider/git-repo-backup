import git


class GitProvider:
    def pull_changes(self, local_repo_path: str) -> None:
        """
        Pull the changes of the remote repository.
        """
        repo = git.cmd.Git(local_repo_path)
        repo.pull()

    def clone_repo(self, remote_url: str, local_repo_path: str) -> None:
        """
        Clones a repository to the disk. Accepts a remote_url and the repo_name.
        """
        git.Git(local_repo_path).clone(remote_url)


class DryRunProvider:
    def pull_changes(self, local_repo_path: str) -> None:
        pass

    def clone_repo(self, remote_url: str, local_repo_path: str) -> None:
        pass

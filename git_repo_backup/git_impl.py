import logging

import git


class GitProvider:
    def pull_changes(self, repo_name: str, local_repo_path: str) -> None:
        """
        Pull the changes of the remote repository.
        """
        logging.info("Pulling changes for '%s'...", repo_name)
        repo = git.cmd.Git(local_repo_path)
        repo.pull()

    def clone_repo(self, remote_url: str, repo_name: str, local_repo_path: str) -> None:
        """
        Clones a repository to the disk. Accepts a remote_url and the repo_name.
        """
        logging.info("Cloning '%s'...", repo_name)
        git.Git(local_repo_path).clone(remote_url)


class DryRunProvider:
    def pull_changes(self, repo_name: str, local_repo_path: str) -> None:
        """
        Pull the changes of the remote repository.
        """
        logging.info("Pulling changes for '%s' in repo %s", repo_name, local_repo_path)

    def clone_repo(self, remote_url: str, repo_name: str, local_repo_path: str) -> None:
        """
        Clones a repository to the disk. Accepts a remote_url and the repo_name.
        """
        logging.info("Cloning '%s' to %s", repo_name, local_repo_path)

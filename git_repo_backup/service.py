from typing import List, Tuple
from repo_filter import RepoFilter

import requests


class Service:
    """
    Abstract class for the hoster.
    """
    service = None
    _username = ""
    repo_filter = None

    def get_service_name(self) -> str:
        """ Returns the identifier of this implementation. """
        return self.service

    def get_user_name(self) -> str:
        """ Returns the username for this implementation. """
        return self._username

    def get_repo_list(self) -> str:
        """ Fetches all the repositories for given user from this service. """
        raise NotImplementedError

    def get_repo_filter(self) -> RepoFilter:
        return self.repo_filter


class Github(Service):
    """
    Hoster implementation for github.com
    """
    service = "Github"

    def __init__(self, username: str, repo_filter: RepoFilter, token=""):
        self._username = username
        self.repo_filter = repo_filter
        self._token = token

    def get_repo_list(self) -> List[Tuple[str, str]]:
        headers = {}
        url = f'https://api.github.com/users/{self._username}/repos?type="owner"&per_page=1000'
        if self._token:
            headers["Authorization"] = f"token {self._token}"
            url = 'https://api.github.com/user/repos?visibility="private"&per_page=1000'

        response = requests.get(headers=headers, url=url)
        if not response.ok:
            return tuple()

        #l = list(map(lambda x: (x["name"], x["clone_url"]), response.json()))
        repos = []
        parsed = response.json()
        for repo in parsed:
            name = repo["name"]
            clone_url = repo["clone_url"]
            if repo["private"] is True:
                clone_url = include_oauth_token_github(clone_url, self._token)
            repos.append((name, clone_url))

        return repos


def include_oauth_token_github(repo_url: str, token: str) -> str:
    repo_url = repo_url.replace("https://", "")
    repo_url = f"https://{token}@{repo_url}"
    return repo_url


class Gitlab(Service):
    """
    Hoster implementation for gitlab.com
    """
    service = "Gitlab"

    def __init__(self, username: str, repo_filter=None, token="", instance="gitlab.com"):
        self._username = username
        self.repo_filter = repo_filter
        self._token = token
        self._instance = instance

    def get_repo_list(self) -> List[Tuple[str, str]]:
        headers = {}
        if self._token:
            headers["PRIVATE-TOKEN"] = self._token

        repos = []
        proceed = True
        page = 1
        while proceed:
            url = f'https://{self._instance}/api/v4/users/{self._username}/projects?page={page}'
            if self._token:
                url = f'https://{self._instance}/api/v4/users/{self._username}/projects?visibility="private"&page={page}'
            response = requests.get(headers=headers, url=url)
            if not response.ok:
                continue

            page += 1
            parsed = response.json()
            proceed = False if len(parsed) == 0 else True
            for repo in parsed:
                name = repo["path"]
                repo_url = repo["http_url_to_repo"]
                if "visibility" in repo and repo["visibility"].lower() == "private":
                    repo_url = include_oauth_token_gitlab(repo_url, self._token)
                repos.append((name, repo_url))

        return repos


def include_oauth_token_gitlab(repo_url: str, token: str) -> str:
    repo_url = repo_url.replace("https://", "")
    repo_url = f"https://oauth2:{token}@{repo_url}"
    return repo_url

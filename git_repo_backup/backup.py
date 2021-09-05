#!/usr/bin/env python3

import argparse
import os
import logging

from typing import List

import requests

from service import Service
from metrics import (
    prom_finish_time,
    prom_ignored_repos,
    prom_error_cnt,
    prom_synced_repos,
    push,
    write_to_textfile,
)


class RepoBackup:
    def __init__(self, services: List[Service], args: argparse.Namespace, git_impl):
        if not services:
            raise ValueError("No services supplied")
        self._services = services

        if not args:
            raise ValueError("No args supplied")
        self._args = args
        self.git_impl = git_impl

        if not os.path.exists(args.dest):
            os.mkdir(args.dest)
        self._dest = args.dest

    def work(self):
        for service in self._services:
            logging.info("Proceeding with service %s", service.get_service_name())
            self.work_service(service)

        prom_finish_time.set_to_current_time()
        if self._args.pushgateway:
            push(self._args.pushgateway)
        elif self._args.prom_file:
            write_to_textfile(self._args.prom_file)

    def get_local_service_dir(self, service: Service) -> str:
        return os.path.join(self._dest, service.get_service_name().lower(), service.get_user_name())

    def get_local_repo_dir(self, service: Service, repo_name: str) -> str:
        local_service_dir = self.get_local_service_dir(service)
        return os.path.join(local_service_dir, repo_name)

    def work_service(self, service):
        """
        Iterates over all the repositories and either clones or pulls the repository.
        """
        local_service_path = self.get_local_service_dir(service)
        if not os.path.isdir(local_service_path):
            os.makedirs(local_service_path)

        repos = None
        try:
            logging.info("Fetching repo list for service %s", service.get_service_name())
            repos = service.get_repo_list()
            logging.info("Fetched %d repos", len(repos))
            if not repos:
                logging.warning("No %s repositories found for username '%s'", service.get_service_name(), service.get_user_name(), )
                return
        except requests.exceptions.RequestException as error:
            logging.error("Error retrieving %s repository for user %s: %s", service.get_service_name(), service.get_user_name(), error)

        self.fetch_repos(repos, service)

    def ignore_repo(self, repo_name: str) -> bool:
        return repo_name in self.deny_list

    def fetch_repos(self, repos: List, service: Service):
        for repo in repos:
            repo_name = repo[0]
            remote_url = repo[1]
            if service.repo_filter.ignore_repo(repo_name):
                prom_ignored_repos.labels(user=service.get_user_name(), provider=service.get_service_name())
                logging.info("Ignoring repo %s", repo_name)
                continue

            try:
                local_repo_dir = self.get_local_repo_dir(service, repo_name)
                if os.path.isdir(local_repo_dir):
                    self.git_impl.pull_changes(repo_name, local_repo_dir)
                    prom_synced_repos.labels(operation="pull", provider=service.get_service_name(), user=service.get_user_name()).inc()
                else:
                    local_service_path = self.get_local_service_dir(service)
                    self.git_impl.clone_repo(remote_url, repo_name, local_service_path)
                    prom_synced_repos.labels(operation="clone", provider=service.get_service_name(), user=service.get_user_name()).inc()

            except Exception as error:
                prom_error_cnt.labels(repo_name=repo_name, provider=service.get_service_name(), user=service.get_user_name()).inc()
                logging.error("Error while synchronizing repo '%s': %s", repo_name, error)

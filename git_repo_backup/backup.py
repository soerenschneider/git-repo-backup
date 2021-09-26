#!/usr/bin/env python3

import argparse
import os
import logging
import concurrent.futures
import time

from datetime import datetime
from typing import List, Tuple, Callable, Any

import requests

from stats import Statistics
from service import Service
from metrics import (
    prom_finish_time,
    prom_receive_repo_list_error_cnt,
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

        dest = os.path.expanduser(args.dest)
        if not os.path.exists(dest):
            os.mkdir(dest)
        self._dest = dest

        self.statistic = Statistics()

    def work(self) -> None:
        max_workers = min(4, len(self._services))
        logging.info("Starting %d workers...", max_workers)
        start_time = datetime.now()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for service in self._services:
                futures.append(executor.submit(self.work_service, service))

            for future in concurrent.futures.as_completed(futures):
                future.result()

        end_time = datetime.now()
        time_taken = f"{format(end_time - start_time)}"
        logging.info("Finished processing %d repos in %s", self.statistic.total, time_taken)
        self.dispatch_metrics()

        if not self._args.daemon:
            self.statistic.display_statistics()

    def work_service(self, service: Service) -> None:
        """
        Iterates over all the repositories and either clones or pulls the repository.
        """
        logging.info("Proceeding with service %s", service.get_service_name())
        local_service_path = self.get_local_service_dir(service)
        if not os.path.isdir(local_service_path):
            os.makedirs(local_service_path)

        repos = None
        try:
            logging.info("Fetching repo list for service %s", service.get_service_name())
            repos = RepoBackup.retry(service.get_repo_list)
            logging.info("Fetched %d repos for provider %s, user %s", len(repos), service.get_service_name(), service.get_user_name())
            if not repos:
                logging.warning("No %s repositories found for username '%s'", service.get_service_name(), service.get_user_name())
                return
        except requests.exceptions.RequestException as error:
            prom_receive_repo_list_error_cnt.labels(user=service.get_user_name(), provider=service.get_service_name()).inc()
            logging.error("Error retrieving %s repository for user %s: %s", service.get_service_name(), service.get_user_name(), error)

        self.fetch_repos(repos, service)

    def fetch_repos(self, repos: List[Tuple[str, str]], service: Service) -> None:
        for repo in repos:
            repo_name = repo[0]
            remote_url = repo[1]
            try:
                RepoBackup.retry(self.fetch_single_repo, (repo_name, remote_url, service,))
            # pylint: disable=broad-except
            except Exception as error:
                self.statistic.repo_error(user=service.get_user_name(), provider=service.get_service_name(), repo_name=repo_name)
                logging.error("Error while synchronizing repo '%s': %s", repo_name, error)

    @staticmethod
    def retry(func: Callable, args=None, max_retries=4) -> Any:
        if not args:
            args = ()

        for i in range(max_retries):
            try:
                return func(*args)
            # pylint: disable=broad-except
            except Exception as err:
                sleep = pow(2, i) - 1
                time.sleep(sleep)
                logging.error("Caught error, retrying %d more times: %s", max_retries - i, err)
                if i == max_retries-1:
                    raise

    def fetch_single_repo(self, repo_name: str, remote_url: str, service: Service) -> None:
        if service.repo_filter.ignore_repo(repo_name):
            self.statistic.repo_ignored(user=service.get_user_name(), provider=service.get_service_name(), repo_name=repo_name)
            logging.info("Ignoring repo %s/%s/%s", service.get_service_name(), service.get_user_name(), repo_name)
            return

        local_repo_dir = self.get_local_repo_dir(service, repo_name)
        if os.path.isdir(local_repo_dir):
            logging.info("Pulling changes for '%s/%s/%s'...", service.get_service_name(), service.get_user_name(), repo_name)
            self.git_impl.pull_changes(local_repo_dir)
            self.statistic.repo_synced(operation="pull", provider=service.get_service_name(), user=service.get_user_name())
        else:
            logging.info("Cloning '%s/%s/%s'...", service.get_service_name(), service.get_user_name(), repo_name)
            local_service_path = self.get_local_service_dir(service)
            self.git_impl.clone_repo(remote_url, local_service_path)
            self.statistic.repo_synced(operation="clone", provider=service.get_service_name(), user=service.get_user_name())

    def get_local_service_dir(self, service: Service) -> str:
        return os.path.join(self._dest, service.get_service_name().lower(), service.get_user_name())

    def get_local_repo_dir(self, service: Service, repo_name: str) -> str:
        local_service_dir = self.get_local_service_dir(service)
        return os.path.join(local_service_dir, repo_name)

    def dispatch_metrics(self) -> None:
        prom_finish_time.set_to_current_time()
        if self._args.pushgateway:
            push(self._args.pushgateway)
        elif self._args.prom_file:
            write_to_textfile(self._args.prom_file)

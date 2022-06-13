import argparse
import logging
import sys
import json
import time

from typing import List, Dict, Optional

from backup import RepoBackup
from service import Service, Github, Gitlab
from git_impl import GitProvider, DryRunProvider
from repo_filter import RepoFilter, AllowListFilter, DenyListFilter, DefaultFilter
from vault import Vault
from metrics import prom_fetch_token_error_cnt, _GIT_BACKUP_REGISTRY

import schedule
from prometheus_client import start_http_server, REGISTRY


def start() -> None:
    setup_logging()
    args = parse_args()
    if not args.config and not args.subparser:
        sys.exit("You must specify a subcommand / config")

    services = []
    if args.config:
        config = read_config(args.config)
        verify_config(config)
        services = build_services_from_conf(config)
    else:
        services = build_services_from_args(args)

    impl = DryRunProvider()
    if not args.dry_run:
        impl = GitProvider()

    fetcher = RepoBackup(services, args, impl)
    fetcher.work()

    if args.daemon:
        if args.prom_port:
            REGISTRY.register(_GIT_BACKUP_REGISTRY)
            start_http_server(args.prom_port)
        schedule.every(24).hours.do(fetcher.work)
        cont = True
        try:
            while cont:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logging.info("Received signal, quitting")
            cont = False

def setup_logging() -> None:
    """ Sets up the logging. """
    loglevel = logging.INFO
    logging.basicConfig(
        level=loglevel, format="%(levelname)s\t %(asctime)s %(message)s"
    )


def parse_args() -> argparse.Namespace:
    """
    Parse all the command line arguments. Returns an initialized Namespace object containing
    all the parsed arugments.
    """
    parser = argparse.ArgumentParser(description="Clones / pulls git repositories")
    subparsers = parser.add_subparsers(dest="subparser")
    parser_github = subparsers.add_parser(Github.service.lower(), help="Github service")
    parser_github.add_argument("-u", "--user", help="Github user name", required=True)

    parser_gitlab = subparsers.add_parser(Gitlab.service.lower(), help="Gitlab service")
    parser_gitlab.add_argument("-u", "--user", help="Gitlab user name", required=True)

    parser.add_argument("-c", "--config", help="Config", action="store",)
    parser.add_argument("-n", "--dry-run", help="Only simulate actions", action="store_true", default=False,)
    parser.add_argument("-d", "--dest", help="Destination to store the repositories", required=True)
    parser.add_argument("--daemon", help="Run as a daemon", action="store_true", default=False)

    prometheus = parser.add_mutually_exclusive_group()
    prometheus.add_argument("-g", "--pushgateway", help="Prometheus pushgateway URL", action="store")
    prometheus.add_argument("-f", "--prom-file", help="Prometheus node_exporter textfile directory", action="store")
    prometheus.add_argument("-p", "--prom-port", type=int, help="Prometheus port to be scraped", default=9155, action="store")

    return parser.parse_args()


def build_services_from_conf(conf: Dict) -> List[Service]:
    services = []
    for service in conf:
        inst = service["service"].lower()
        del service["service"]

        repo_filter = build_filter_from_conf(service)
        if "repo_denylist" in service:
            del service["repo_denylist"]
        if "repo_allowlist" in service:
            del service["repo_allowlist"]
        service["repo_filter"] = repo_filter

        if "token" in service and "vault" in service:
            raise ValueError("Both 'token' and 'vault' specified, must only use one source for tokens")

        if "vault" in service:
            token = read_token_from_vault(service["vault"], inst, service["username"])
            if token:
                service["token"] = token
            del service["vault"]

        if inst == "github":
            impl = Github(**service)
            services.append(impl)
        elif inst == "gitlab":
            impl = Gitlab(**service)
            services.append(impl)

    return services


def read_token_from_vault(conf: Dict, service: str, username: str) -> Optional[str]:
    try:
        vault = Vault(**conf)
        token = vault.read_secret()
        return token
    except Exception as err:
        prom_fetch_token_error_cnt.labels(user=username, provider=service).inc()
        logging.error("Could not extract token from vault: ", err)
    return None


def read_config(file_name: str) -> Dict:
    with open(file_name, 'r', encoding="utf-8") as opened:
        return json.load(opened)
    return None


def verify_config(conf: Dict):
    if len(conf) == 0:
        raise ValueError("No services defined")
    keywords = ["service", "username"]

    for service in conf:
        for keyword in keywords:
            if keyword not in service:
                raise ValueError

    if "repo_denylist" in conf and "repo_allowlist" in conf:
        raise ValueError("Can't define both allow- and denylists")


def build_filter_from_conf(conf: Dict) -> RepoFilter:
    if "repo_denylist" in conf:
        return DenyListFilter(conf["repo_denylist"])

    if "repo_allowlist" in conf:
        return AllowListFilter(conf["repo_allowlist"])

    return DefaultFilter()


def build_services_from_args(args: argparse.Namespace) -> List[Service]:
    services = []
    if args.subparser == Gitlab.service.lower():
        services.append(Gitlab(args.user, repo_filter=DefaultFilter()))

    elif args.subparser == Github.service.lower():
        services.append(Github(args.user, repo_filter=DefaultFilter()))

    return services

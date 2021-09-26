import os
from prometheus_client import (
    Counter,
    Gauge,
    CollectorRegistry,
    push_to_gateway as _push_to_gateway,
    write_to_textfile as _write_to_textfile,
)

_REGISTRY = CollectorRegistry()
NAMESPACE = "git_repository_syncer"


prom_fetch_token_error_cnt = Counter(
    namespace=NAMESPACE,
    name="vault_token_fetch_errors_total",
    documentation="Amount of errors while trying to fetch secret token from vault",
    labelnames=["user", "provider"],
    registry=_REGISTRY,
)


prom_receive_repo_list_error_cnt = Counter(
    namespace=NAMESPACE,
    name="repolist_errors_total",
    documentation="Amount of errors while listing repos",
    labelnames=["user", "provider"],
    registry=_REGISTRY,
)

prom_synced_repos = Counter(
    namespace=NAMESPACE,
    name="synced_repos_total",
    documentation="Amount of repositories fetched",
    labelnames=["user", "provider", "operation"],
    registry=_REGISTRY,
)

prom_ignored_repos = Counter(
    namespace=NAMESPACE,
    name="ignored_repos_total",
    documentation="Amount of ignored repositories",
    labelnames=["user", "provider", "repo"],
    registry=_REGISTRY,
)

prom_sync_error_cnt = Counter(
    namespace=NAMESPACE,
    name="synced_repos_errors_total",
    documentation="Amount of errors while fetching repo",
    labelnames=["user", "provider", "repo"],
    registry=_REGISTRY,
)

prom_finish_time = Gauge(
    namespace=NAMESPACE,
    name="finished_timestamp_seconds",
    documentation="Timestamp when synchronization finished",
    registry=_REGISTRY,
)


def write_to_textfile(prom_file: str) -> None:
    """
    Writes the metrics to the nodeexporter textfile directory. Accepts
    a full path to write the metrics file to.
    """
    if not prom_file:
        raise ValueError("prom_file can not be empty")

    prom_dir = os.path.dirname(prom_file)
    if not os.path.exists(prom_dir):
        raise ValueError("Dir {} does not exist".format(prom_dir))

    _write_to_textfile(prom_file, _REGISTRY)


def push(gateway: str, job=None) -> None:
    """
    Pushes the metrics to a prometheus pushgateway. Accepts the hostname
    of the pushgateway.
    """
    if not gateway:
        raise ValueError("No gateway defined")

    if not job:
        job = "repo_replicator"

    _push_to_gateway(gateway, job=job, registry=_REGISTRY)

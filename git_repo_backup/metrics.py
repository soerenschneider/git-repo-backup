import os
from prometheus_client import (
    Counter,
    Gauge,
    CollectorRegistry,
    push_to_gateway as _push_to_gateway,
    write_to_textfile as _write_to_textfile,
)

_REGISTRY = CollectorRegistry()
_PREFIX = "git_repository_syncer"

prom_synced_repos = Counter(
    "{prefix}_synced_repos_total".format(prefix=_PREFIX),
    "Amount of repositories fetched",
    ["user", "provider", "operation"],
    registry=_REGISTRY,
)

prom_error_cnt = Counter(
    "{prefix}_synced_repos_errors_total".format(prefix=_PREFIX),
    "Amount of errors while fetching repo",
    ["user", "provider", "repo_name"],
    registry=_REGISTRY,
)

prom_finish_time = Gauge(
    "{prefix}_finished_timestamp_seconds".format(prefix=_PREFIX),
    "Timestamp when synchronization finished",
    registry=_REGISTRY,
)


def write_to_textfile(prom_file):
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


def push(gateway, job=None):
    """
    Pushes the metrics to a prometheus pushgateway. Accepts the hostname
    of the pushgateway.
    """
    if not gateway:
        raise ValueError("No gateway defined")

    if not job:
        job = "repo_replicator"

    _push_to_gateway(gateway, job=job, registry=_REGISTRY)

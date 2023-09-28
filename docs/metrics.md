# Metrics

## Metrics Exposition
Metrics can be exposed by 
- starting a http server and be scraped by Prometheus as a separate target
- defining a Pushgateway host
- dumping the metrics as text to the node_exporter textfile collector directory

Check the [Prometheus configuration section](configuration.md#prometheus-options) for more info.

## Metrics Overview
All metrics are prefixed with `git_repository_syncer`

| Metric Name                           | Description                                                    | Labels                                      |
|---------------------------------------|----------------------------------------------------------------|---------------------------------------------|
| vault_token_fetch_errors_total        | Amount of errors while trying to fetch secret token from vault | user, provider                              |
| repolist_errors_total                 | Amount of errors while listing repos                           | user, provider                              |
| synced_repos_total                    | Amount of repositories fetched                                 | user, provider, operation                   |
| ignored_repos_total                   | Amount of ignored repositories                                 | user, provider, repo                        |
| synced_repos_errors_total             | Amount of errors while fetching repo                           | user, provider, repo                        |
| finished_timestamp_seconds (Gauge)    | Timestamp when synchronization finished                        |                                             |

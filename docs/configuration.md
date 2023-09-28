# Configuration

## CLI Arguments
It's possible to run git-repo-backup solely through CLI args. To leverage all available configuration options it's however necessary to create a config file.

### Available Subcommands

- `github`: Perform operations on GitHub repositories.
    - `-u, --user`: GitHub username (required).

- `gitlab`: Perform operations on GitLab repositories.
    - `-u, --user`: GitLab username (required).

### Common Options

- `-c, --config`: Path to the configuration file.
- `-n, --dry-run`: Simulate actions without making actual changes (default: `False`).
- `-d, --dest`: Destination directory to store the repositories (required).
- `--daemon`: Run the Git Repository Syncer as a daemon (default: `False`).

### Prometheus Options

You can choose one of the following options for Prometheus metrics:

- `-g, --pushgateway`: Prometheus Pushgateway URL.
- `-f, --prom-file`: Directory for Prometheus Node Exporter textfile collector.
- `-p, --prom-port`: Prometheus port to be exposed (default: 9155).

These options allow you to configure Prometheus metrics for monitoring and reporting.


## Via Config File

### Examplary Config file
```json
[
  {
    "service": "github",
    "username": "soerenschneider",
    "repo_denylist": [
      "lootorganizer"
    ]
  },
  {
    "service": "gitlab",
    "username": "soerenschneider",
    "repo_allowlist": [
      "prometheus-rules-edge"
    ]
  }
]
```

# git-repo-backup
![test-workflow](https://github.com/soerenschneider/git-repo-backup/actions/workflows/test.yaml/badge.svg)
![release-workflow](https://github.com/soerenschneider/git-repo-backup/actions/workflows/release.yaml/badge.svg)

Automated and reliable backups of your GitHub and GitLab repositories

## Features

📦 Backups remote Git repositories hosted on GitLab or GitHub<br/>
⛵️ Automatically discovers all repositories for a given username<br/>
🕵️ Works with public and private repositories<br/>
🚦 Support for explicit deny- and allow-lists<br/>
🔒 Can read Personal Access Tokens from Hashicorp Vault<br/>
🔭 Observability provided by metrics<br/>

## Roadmap

🚀 Upload changes to a S3 compatible service<br/>
🍵 Add GitTea service support
🪆 Add _dummy service_ that allows a plain list of loose Git repositories 

## Why would I need this?

GitHub and GitLab don't run on altruism. Your account or individual repositories may be gone overnight without notice.

## Installation

### Docker / Podman
````shell
$ git clone https://github.com/soerenschneider/git-repo-backup.git
$ cd git-repo-backup
$ docker run -v $(pwd)/contrib:/config ghcr.io/soerenschneider/git-repo-backup --config /config/example-config.json --dest /tmp
````

### From Source
As a prerequisite, you need to have Python3 installed.
```shell
$ git clone https://github.com/soerenschneider/git-repo-backup.git
$ cd git-repo-backup
$ make venv
$ ./venv/bin/python3 git_repo_backup --config contrib/example-config.json --dest /tmp
```

# Demo
![demo.gif](demo.gif)

# Usage and Configuration
Head over [here](docs/configuration.md) to see config and usage examples.

# Metrics
The exposed metrics are listed [here](docs/metrics.md).

## Changelog
See the [full changelog](CHANGELOG.md)
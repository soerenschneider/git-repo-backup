
# What


# Why
Neither is Git a viable backup nor will GitHub/Gitlab keep your repos around forever. This tool helps you auto-discover and regularly pull your git repositories from Git services such as GitHub and GitLab.

# Demo
![demo.gif](demo.gif)

# CLI Example
```
usage: cmd.py [-h] [-c CONFIG] [-n] -d DEST [-g PUSHGATEWAY | -f PROM_FILE] {github,gitlab} ...

Clones / pulls git repositories

positional arguments:
  {github,gitlab}
    github              Github service
    gitlab              Gitlab service

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Config
  -n, --dry-run         Only simulate actions
  -d DEST, --dest DEST  Destination to store the repositories
  -g PUSHGATEWAY, --pushgateway PUSHGATEWAY
                        Prometheus pushgateway URL
  -f PROM_FILE, --prom-file PROM_FILE
                        Prometheus nodeexporter textfile directory
```

# Configuration

````json
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
````
# Services monitoring

[![Project Status: Abandoned – Initial development has started, but there has not yet been a stable, usable release; the project has been abandoned and the author(s) do not intend on continuing development.](https://www.repostatus.org/badges/latest/abandoned.svg)](https://www.repostatus.org/#abandoned)

:warning: **This tool is no longer maintained**

You may want to have a look to [go-monitoring](https://github.com/the-kube-way/go-monitoring/) for an alternative.

Python-based tool for monitoring the status of various services.

### Probes
- ping: test if host is up
- raw_tcp: test if a service is running on that port or not (protocol abstraction)
- https: do various checks (status code, cert expiration, TLSA, etc) on HTTP(S) webserver
- smtp: check if smtp server is working (including STARTTLS handshake and TLSA)
- dns: check if all NS servers are up and if DNSSEC is valid

### Notification channels
- email

## Command-line usage
Install dependencies using:
```bash
pip3 install --user -r requirements.txt
```
Run the program:
```bash
python3 monitoring.py -c config.yaml
```

## Docker usage
Building is simple and may be done locally (ideally after [checking GPG commit signature](https://github.com/selfhosting-tools/master-keys)).
```bash
git clone --depth 1 https://github.com/selfhosting-tools/services-monitoring.git
git -C services-monitoring verify-commit HEAD
cp services-monitoring/docker/docker-compose.yaml .
docker-compose build
```
Patch `docker-compose.yaml` to your own path for config directory if needed (default to ./config).  
Put your config files in your config directory. 
All config files in the config directory will be run in parallel.  
Finally start the container:
```bash
docker-compose up -d
```

## Configuration file format
See `example.yaml`.

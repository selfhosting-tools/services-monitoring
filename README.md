# Services monitoring

[![Build Status](https://travis-ci.org/selfhosting-tools/services-monitoring.svg?branch=master)](https://travis-ci.org/selfhosting-tools/services-monitoring)

Python-based tool for monitoring the status of various services.

## Probes
- ping: test if host is up
- raw_tcp: test if a service is running on that port or not (protocol abstraction)
- https: do various checks (status code, cert expiration, etc) on HTTP webserver
- smtp: check if smtp server is working (including STARTTLS handshake)
- dns: check if all NS servers are up

## Notification channels
- email

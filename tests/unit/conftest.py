"""Unit-test runtime guards for flext-db-oracle."""

from __future__ import annotations

import socket

# Prevent unit tests from hanging on network failures.
socket.setdefaulttimeout(2)

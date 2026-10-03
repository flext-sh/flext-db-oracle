"""Unit-test runtime guards for flext-db-oracle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import socket

# Prevent unit tests from hanging on network failures.
socket.setdefaulttimeout(2)

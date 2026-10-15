#!/usr/bin/env python3
"""Cursor Subagent Start Hook.

This hook handles the start event for the cursor subagent.
It validates the input payload and returns an appropriate response.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import json
import sys

payload = json.load(sys.stdin)
if not isinstance(payload, dict):
    msg = "hook input must be a JSON object"
    raise TypeError(msg)
response = json.loads('{"permission":"allow"}')
json.dump(response, sys.stdout, ensure_ascii=False, separators=(",", ":"))
sys.stdout.write("\n")

# -*- coding: utf-8 -*-
"""Convenience runner for the knowledge_updater test suite.

    python tools/tests/run.py            # run pytest quietly
    python tools/tests/run.py -v         # verbose
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import pytest  # noqa: E402

if __name__ == "__main__":
    args = [os.path.join(HERE, "test_knowledge_updater.py")]
    if "-v" in sys.argv:
        args.append("-v")
    else:
        args.append("-q")
    sys.exit(pytest.main(args))

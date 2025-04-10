#!/usr/bin/env python
import pytest
import sys

if __name__ == "__main__":
    # Run pytest with the provided arguments or default to running all tests
    sys.exit(pytest.main(sys.argv[1:] or ["tests"])) 
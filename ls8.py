#!/usr/bin/env python3

"""Main."""

import sys
from cpu import CPU

if len(sys.argv) != 2:
    print("Must provide a filename")
else:

    cpu = CPU()

    cpu.load(sys.argv[1])
    cpu.run()
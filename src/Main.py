#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main application launcher for Pars Update.
Runs modern GTK4 / Libadwaita architecture.
"""

import os
import sys

# Ensure src/ directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    import MainAdw
    return MainAdw.main()


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto package cache update script for Pars Update.
Supports Debian/APT and Arch Linux/Pacman.
"""

import os
import subprocess

from PackageManagerBackend import get_package_manager


def main():
    backend = get_package_manager()
    if backend == "pacman":
        subprocess.call(["pacman", "-Sy"],
                        env={**os.environ, 'LC_ALL': 'C'})
    else:
        subprocess.call(["apt", "update"],
                        env={**os.environ,
                             'DEBIAN_FRONTEND': 'noninteractive',
                             'LC_ALL': 'C'})


if __name__ == "__main__":
    main()

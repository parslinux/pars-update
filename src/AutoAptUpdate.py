#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto package cache update script for Pars Update.
Supports Debian/APT and Arch Linux/Pacman.
"""

import os
import shutil
import subprocess
import sys

from PackageManagerBackend import get_package_manager


def main():
    backend = get_package_manager()
    if backend == "pacman":
        if shutil.which("checkupdates"):
            res = subprocess.call(["checkupdates", "--nocolor"],
                                  env={**os.environ, 'LC_ALL': 'C'})
            # checkupdates returns 0 (updates available) or 2 (no updates)
            sys.exit(0 if res in (0, 2) else res)
        else:
            res = subprocess.call(["pacman", "-Qu"],
                                  env={**os.environ, 'LC_ALL': 'C'})
            # pacman -Qu returns 0 (updates available) or 1 (no updates)
            sys.exit(0 if res in (0, 1) else res)
    else:
        res = subprocess.call(["apt", "update"],
                              env={**os.environ,
                                   'DEBIAN_FRONTEND': 'noninteractive',
                                   'LC_ALL': 'C'})
        sys.exit(res)


if __name__ == "__main__":
    main()

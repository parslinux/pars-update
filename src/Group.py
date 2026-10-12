#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User and group management helper for Pars Update.
Distro-agnostic implementation supporting Arch Linux, Debian, and other Linux distributions.
"""

import grp
import shutil
import subprocess
import sys


def ensure_group():
    try:
        grp.getgrnam("pars-update")
    except KeyError:
        if shutil.which("groupadd"):
            subprocess.run(["groupadd", "-r", "pars-update"], check=True)
        elif shutil.which("addgroup"):
            subprocess.run(["addgroup", "--system", "pars-update"], check=True)


def main():
    def addtogroup(user):
        ensure_group()
        if shutil.which("gpasswd"):
            return subprocess.call(["gpasswd", "-a", user, "pars-update"])
        elif shutil.which("usermod"):
            return subprocess.call(["usermod", "-aG", "pars-update", user])
        elif shutil.which("adduser"):
            return subprocess.call(["adduser", user, "pars-update"])
        else:
            print("No suitable user management tool found (gpasswd/usermod/adduser)", file=sys.stderr)
            return 1

    def delfromgroup(user):
        if shutil.which("gpasswd"):
            return subprocess.call(["gpasswd", "-d", user, "pars-update"])
        elif shutil.which("deluser"):
            return subprocess.call(["deluser", user, "pars-update"])
        else:
            print("No suitable user management tool found (gpasswd/deluser)", file=sys.stderr)
            return 1

    if len(sys.argv) > 2:
        if sys.argv[1] == "add":
            sys.exit(addtogroup(sys.argv[2]))
        elif sys.argv[1] == "del":
            sys.exit(delfromgroup(sys.argv[2]))
        else:
            print("unknown argument error", file=sys.stderr)
            sys.exit(1)
    else:
        print("no argument passed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

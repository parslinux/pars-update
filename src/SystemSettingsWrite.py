#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System configuration writer executed via pkexec for Pars Update.
Ensures configuration directory exists and writes system parameters.
"""

import os
import sys
from configparser import ConfigParser


def main():
    configdir = "/etc/pars/"
    configfile = "pars-update.conf"
    config = ConfigParser(strict=False)

    def write_lastupdate(timestamp):
        os.makedirs(configdir, exist_ok=True)
        config_path = os.path.join(configdir, configfile)
        if os.path.exists(config_path):
            config.read(config_path)

        if config.has_section("Update"):
            config.set("Update", "lastupdate", timestamp)
        else:
            config['Update'] = {"lastupdate": timestamp}

        with open(config_path, "w") as cf:
            config.write(cf)

    def validate_timestamp(value):
        try:
            ts = int(value)
            if ts < 0:
                raise ValueError
            return str(ts)
        except ValueError:
            raise ValueError("Invalid timestamp")

    if len(sys.argv) > 2:
        if sys.argv[1] == "write":
            if sys.argv[2] == "lastupdate":
                write_lastupdate(validate_timestamp(sys.argv[3]))
        else:
            print("unknown argument error")
    else:
        print("no argument passed")


if __name__ == "__main__":
    main()

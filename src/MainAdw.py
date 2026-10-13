#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main application entrypoint using GTK4 and Libadwaita for Pars Update.
"""

import os
import sys

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib

# Ensure src/ is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.MainWindowAdw import MainWindowAdw


class UpdateApplication(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="org.pars.update",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        self.window = None
        self.args = {}
        GLib.set_prgname("org.pars.update")

        self.add_main_option(
            "tray",
            ord("t"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Start application in tray/background mode",
            None,
        )
        self.add_main_option(
            "check",
            ord("c"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Check for updates in background without raising window",
            None,
        )
        self.add_main_option(
            "page",
            ord("p"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.STRING,
            "Start application on specified page (e.g. updates, settings)",
            None,
        )

    def do_activate(self):
        if not self.window:
            self.window = MainWindowAdw(self)

        self.window.handle_args(self.args)

        is_background = self.args.get("tray") or self.args.get("check")
        if not is_background:
            self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        self.args = options.end().unpack()
        self.activate()
        return 0


def main():
    app = UpdateApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main application launcher for Pars Update.
Supports modern GTK4 / Libadwaita by default, with automatic or explicit fallback to GTK3 legacy UI.
"""

import os
import sys

# Ensure src/ directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_gtk3():
    """Fallback runner for legacy GTK3 MainWindow."""
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gio, GLib
    from MainWindow import MainWindow

    class LegacyApplication(Gtk.Application):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, application_id="org.pars.update",
                             flags=Gio.ApplicationFlags(8), **kwargs)
            self.window = None
            self.args = {}
            GLib.set_prgname("org.pars.update")

            self.add_main_option(
                "tray",
                ord("t"),
                GLib.OptionFlags(0),
                GLib.OptionArg(0),
                "Start application on tray mode",
                None,
            )
            self.add_main_option(
                "page",
                ord("p"),
                GLib.OptionFlags(0),
                GLib.OptionArg(1),
                "Start application on specified page",
                None,
            )

        def do_activate(self):
            if not self.window:
                self.window = MainWindow(self)
            else:
                self.window.control_args()
                self.window.main_window.present()

        def do_command_line(self, command_line):
            options = command_line.get_options_dict()
            options = options.end().unpack()
            self.args = options
            self.activate()
            return 0

    app = LegacyApplication()
    return app.run(sys.argv)


def main():
    force_gtk3 = False
    if "--gtk3" in sys.argv:
        sys.argv.remove("--gtk3")
        force_gtk3 = True
    elif "--legacy" in sys.argv:
        sys.argv.remove("--legacy")
        force_gtk3 = True

    if force_gtk3:
        return run_gtk3()

    try:
        import gi
        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        import MainAdw
        return MainAdw.main()
    except Exception as e:
        print(f"Notice: GTK4/Libadwaita not available ({e}), falling back to GTK3 legacy UI.")
        return run_gtk3()


if __name__ == "__main__":
    sys.exit(main())

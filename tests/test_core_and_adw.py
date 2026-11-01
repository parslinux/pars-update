#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for Pars Update core layer and modern Libadwaita architecture.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure src/ is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.ConfigManager import ConfigManager
from core.NotificationManager import NotificationManager
from core.TerminalRunner import TerminalRunner
from core.UpdateEngine import UpdateEngine


class TestCoreArchitecture(unittest.TestCase):
    def setUp(self):
        self.engine = UpdateEngine()
        self.config = ConfigManager()
        self.notifications = NotificationManager()

    def test_update_engine_initialization(self):
        self.assertIsNotNone(self.engine.backend)
        self.assertIn(self.engine.backend_name, ("pacman", "apt"))
        locked, msg = self.engine.is_locked()
        self.assertIsInstance(locked, bool)

    def test_update_engine_calculate_sizes(self):
        sizes = self.engine.calculate_sizes(keep_list=[])
        self.assertIn("download_size", sizes)
        self.assertIn("install_size", sizes)
        self.assertIn("download_size_str", sizes)
        self.assertIn("install_size_str", sizes)
        self.assertIn("to_upgrade", sizes)
        self.assertIn("to_keep", sizes)

    def test_update_engine_sources_and_orphans(self):
        sources = self.engine.get_sources()
        self.assertIsInstance(sources, dict)
        orphans = self.engine.get_orphans()
        self.assertIsInstance(orphans, list)

    def test_update_engine_requires_reboot(self):
        self.assertTrue(self.engine.requires_reboot("linux"))
        self.assertTrue(self.engine.requires_reboot("linux-lts"))
        self.assertTrue(self.engine.requires_reboot("linux-zen"))
        self.assertTrue(self.engine.requires_reboot("linux-image-6.1.0-amd64"))
        self.assertTrue(self.engine.requires_reboot("glibc"))
        self.assertFalse(self.engine.requires_reboot("curl"))
        self.assertFalse(self.engine.requires_reboot("nano"))

    def test_update_engine_get_package_details(self):
        details = self.engine.get_package_details("curl")
        self.assertIsInstance(details, dict)
        self.assertEqual(details["name"], "curl")
        self.assertIn("version", details)
        self.assertIn("description", details)
        self.assertIn("url", details)
        self.assertIn("changelog", details)
        self.assertIn("requires_reboot", details)
        self.assertFalse(details["requires_reboot"])

    def test_config_manager_properties(self):
        original_interval = self.config.interval
        self.config.interval = 86400
        self.assertEqual(self.config.interval, 86400)

        original_autostart = self.config.autostart
        self.config.autostart = not original_autostart
        self.assertEqual(self.config.autostart, not original_autostart)
        # Restore
        self.config.autostart = original_autostart
        self.config.interval = original_interval

        orig_metered = self.config.pause_on_metered
        self.config.pause_on_metered = not orig_metered
        self.assertEqual(self.config.pause_on_metered, not orig_metered)
        self.config.pause_on_metered = orig_metered

    def test_network_monitor_initialization(self):
        from core.NetworkMonitor import NetworkMonitor
        net = NetworkMonitor()
        self.assertIsInstance(net.is_connected, bool)
        self.assertIsInstance(net.is_metered, bool)
        self.assertIsInstance(net.connectivity, int)
        dummy_cb = lambda c, m: None
        net.add_listener(dummy_cb)
        self.assertIn(dummy_cb, net._listeners)
        net.remove_listener(dummy_cb)
        self.assertNotIn(dummy_cb, net._listeners)

    def test_config_manager_record_update(self):
        self.config.record_update_now()
        self.assertGreater(self.config.last_update, 0)

    def test_notification_manager_safeguards(self):
        # Should not raise exception even without active notification daemon
        try:
            self.notifications.notify_updates_available(3, ["curl", "git", "vim"])
            self.notifications.notify_completed()
            self.notifications.notify_error("Simulated lock error")
        except Exception as e:
            self.fail(f"NotificationManager raised unexpected exception: {e}")

    def test_terminal_runner_safeguard(self):
        runner = TerminalRunner()
        # Spawning with None terminal should gracefully return False without crashing
        res = runner.spawn(None, ["echo", "test"])
        self.assertFalse(res)


class TestAdwUIImports(unittest.TestCase):
    def test_adw_ui_imports(self):
        try:
            import gi
            gi.require_version("Gtk", "4.0")
            gi.require_version("Adw", "1")
            from gi.repository import Adw, Gtk
            from ui.PreferencesAdw import PreferencesAdw
            from ui.MainWindowAdw import MainWindowAdw
            from MainAdw import UpdateApplication
            self.assertTrue(True)
        except (ValueError, ImportError) as e:
            self.skipTest(f"GTK4 / Libadwaita environment not available: {e}")

    def test_main_cli_options(self):
        try:
            import gi
            gi.require_version("Gtk", "4.0")
            gi.require_version("Adw", "1")
            from MainAdw import UpdateApplication
            app = UpdateApplication()
            self.assertEqual(app.get_application_id(), "org.pars.update")
        except (ValueError, ImportError) as e:
            self.skipTest(f"GTK4 / Libadwaita environment not available: {e}")

    def test_main_window_populate_and_clear_updates(self):
        try:
            import gi
            gi.require_version("Gtk", "4.0")
            gi.require_version("Adw", "1")
            from gi.repository import Adw, Gtk
            from MainAdw import UpdateApplication
            from ui.MainWindowAdw import MainWindowAdw
            Adw.init()
            win = MainWindowAdw(application=None)
            fake_updates = [
                {"name": "test-pkg1", "old_version": "1.0", "new_version": "1.1", "size_str": "1 MB"},
                {"name": "test-pkg2", "old_version": "2.0", "new_version": "2.1", "size_str": "2 MB"}
            ]
            win._populate_updates_view(fake_updates)
            self.assertEqual(len(win.update_rows), 2)
            # Re-populating should clear previous rows without any AdwPreferencesGroup critical error
            win._populate_updates_view([fake_updates[0]])
            self.assertEqual(len(win.update_rows), 1)
            win._clear_updates_view()
            self.assertEqual(len(win.update_rows), 0)
        except (ValueError, ImportError) as e:
            self.skipTest(f"GTK4 / Libadwaita environment not available: {e}")


if __name__ == "__main__":
    unittest.main()

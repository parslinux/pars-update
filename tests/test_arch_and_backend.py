#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Pars Update (Arch Linux integration, Backend & SVG assets).
"""

import os
import sys
import unittest
import xml.etree.ElementTree as ET

# Ensure src/ is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PackageManagerBackend import (
    get_distro_info,
    get_package_manager,
    parse_pacman_size_str,
    PacmanBackend
)


class TestPackageManagerBackend(unittest.TestCase):
    def setUp(self):
        self.backend = PacmanBackend()

    def test_distro_info_detection(self):
        info = get_distro_info()
        self.assertIn("id", info)
        self.assertIn("package_manager", info)
        self.assertIn(info["package_manager"], ("pacman", "apt"))

    def test_parse_pacman_size_str(self):
        self.assertEqual(parse_pacman_size_str("100 B"), 100)
        self.assertEqual(parse_pacman_size_str("1 KiB"), 1024)
        self.assertEqual(parse_pacman_size_str("1 MiB"), 1024 * 1024)
        self.assertEqual(parse_pacman_size_str("2.5 GiB"), int(2.5 * 1024 * 1024 * 1024))
        self.assertEqual(parse_pacman_size_str(""), 0)
        self.assertEqual(parse_pacman_size_str(None), 0)

    def test_pacman_version_compare(self):
        self.assertEqual(self.backend.versionCompare("1.0.0", "1.0.0"), 0)
        self.assertEqual(self.backend.versionCompare("1.0.1", "1.0.0"), 1)
        self.assertEqual(self.backend.versionCompare("1.0.0", "1.0.1"), -1)

    def test_pacman_beauty_size(self):
        s1 = self.backend.beauty_size(1024)
        s0 = self.backend.beauty_size(0)
        self.assertTrue('B' in s1 or 'b' in s1)
        self.assertTrue('0' in s0)

    def test_desktop_file_resolution(self):
        # Test resolving standard system desktop file
        success, pkg = self.backend.get_appname_from_desktopfile("nonexistent-app-123.desktop")
        self.assertFalse(success)
        self.assertEqual(pkg, "")

    def test_package_class_wrappers(self):
        from Package import Package
        pkg_obj = Package()
        self.assertTrue(hasattr(pkg_obj, "control_lock"))
        self.assertTrue(hasattr(pkg_obj, "required_changes"))
        locked, msg = pkg_obj.control_lock()
        self.assertIsInstance(locked, bool)
        rc = pkg_obj.required_changes("curl", sleep=False)
        self.assertIn("to_delete", rc)
        self.assertFalse(pkg_obj.versionCompare(None, "1.0"))
        self.assertFalse(pkg_obj.versionCompare("1.0", None))

    def test_pacman_batch_query_resilience(self):
        self.backend._query_pacman_si_batch(["nonexistent_pkg_12345"])
        info = self.backend._query_pacman_si("nonexistent_pkg_12345")
        self.assertEqual(info["name"], "nonexistent_pkg_12345")
        self.assertEqual(info["version"], "")


class TestSvgAssets(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        self.svg_files = [
            "pars-update.svg",
            "pars-update-symbolic.svg",
            "pars-update-available-symbolic.svg",
            "pars-update-inprogress-symbolic.svg",
            "pars-update-error-symbolic.svg",
            "pars-update-uptodate.svg",
            "pars-update-cantconnect.svg",
        ]

    def test_svg_files_valid_xml(self):
        for svg_name in self.svg_files:
            file_path = os.path.join(self.data_dir, svg_name)
            self.assertTrue(os.path.exists(file_path), f"{svg_name} must exist")
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                self.assertIn("svg", root.tag.lower(), f"{svg_name} root tag must be svg")
                self.assertTrue(root.attrib.get("viewBox") or (root.attrib.get("width") and root.attrib.get("height")),
                                f"{svg_name} must define viewBox or dimensions")
            except ET.ParseError as e:
                self.fail(f"Invalid XML syntax in {svg_name}: {e}")

    def test_policykit_policy_xml(self):
        policy_path = os.path.join(self.data_dir, "org.pars.pkexec.pars-update.policy")
        self.assertTrue(os.path.exists(policy_path))
        tree = ET.parse(policy_path)
        root = tree.getroot()
        self.assertEqual(root.tag, "policyconfig")

    def test_style_css(self):
        css_path = os.path.join(self.data_dir, "style.css")
        self.assertTrue(os.path.exists(css_path))
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn(".pars-update-frame", content)
        self.assertIn(".suggested-action", content)
        self.assertIn(".destructive-action", content)


if __name__ == "__main__":
    unittest.main()

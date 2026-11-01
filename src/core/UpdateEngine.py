#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core update engine for Pars Update.
Decoupled from UI, handles package manager operations for both Arch Linux and Debian/Pars.
"""

import logging
import os
import re
import subprocess
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple

import gi
from gi.repository import GLib

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PackageManagerBackend import get_package_manager, PacmanBackend

logger = logging.getLogger("pars-update-engine")


class UpdateEngine:
    """Manages update checking, size calculations, and cache state."""

    def __init__(self) -> None:
        self.backend_name: str = get_package_manager()
        self.backend: Any = None
        self._init_backend()

        self._upgrades_cache: Dict[str, Dict[str, Any]] = {}
        self._is_checking: bool = False

    def _init_backend(self) -> None:
        if self.backend_name == "pacman":
            self.backend = PacmanBackend()
        else:
            try:
                import apt
                from Package import Package
                self.backend = Package()
            except Exception as e:
                logger.warning("Could not initialize Package() backend: %s. Using Pacman/Fallback.", e)
                self.backend = PacmanBackend()

    def is_locked(self) -> Tuple[bool, str]:
        """Checks if package manager is locked by another process."""
        if hasattr(self.backend, "control_lock"):
            ok, msg = self.backend.control_lock()
            return (not ok), msg
        return False, ""

    REBOOT_PATTERNS = [
        r"^linux(-lts|-zen|-hardened)?$",
        r"^linux-firmware$",
        r"^linux-image-",
        r"^linux-headers-",
        r"^glibc$",
        r"^libc6$",
        r"^systemd(-libs)?$",
        r"^udev$",
    ]

    def requires_reboot(self, pkg_name: str) -> bool:
        """Determines if a package upgrade requires a system reboot."""
        for pattern in self.REBOOT_PATTERNS:
            if re.search(pattern, pkg_name, re.IGNORECASE):
                return True
        return False

    def check_updates(self) -> List[Dict[str, Any]]:
        """Synchronously check for available updates and return list of package details."""
        self._is_checking = True
        try:
            self.backend.updatecache()
            upgradables = self.backend.upgradable()
            results: List[Dict[str, Any]] = []

            # Batch query for speed if supported
            if hasattr(self.backend, "_query_pacman_si_batch"):
                self.backend._query_pacman_si_batch(upgradables)

            for pkg in upgradables:
                old_v = self.backend.installed_version(pkg)
                new_v = self.backend.candidate_version(pkg)
                desc = self.backend.summary(pkg)
                size_str = self.backend.size(pkg)

                results.append({
                    "name": pkg,
                    "old_version": old_v,
                    "new_version": new_v,
                    "summary": desc,
                    "size_str": size_str,
                    "section": getattr(self.backend, "get_section", lambda x: "")(pkg),
                    "requires_reboot": self.requires_reboot(pkg),
                })

            return results
        finally:
            self._is_checking = False

    def check_updates_async(self, callback: Callable[[List[Dict[str, Any]], Optional[Exception]], None]) -> None:
        """Asynchronously check for updates in a worker thread and invoke callback on main GLib loop."""
        def worker() -> None:
            try:
                updates = self.check_updates()
                GLib.idle_add(callback, updates, None)
            except Exception as e:
                logger.error("Error in check_updates_async: %s", e)
                GLib.idle_add(callback, [], e)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def calculate_sizes(self, keep_list: Optional[List[str]] = None) -> Dict[str, Any]:
        """Calculate download and install sizes for current upgradable packages."""
        if hasattr(self.backend, "required_changes_upgrade"):
            rcu = self.backend.required_changes_upgrade(sleep=False, keep_list=keep_list)
            return {
                "download_size": rcu.get("download_size", 0),
                "install_size": rcu.get("install_size", 0),
                "download_size_str": self.backend.beauty_size(rcu.get("download_size", 0)),
                "install_size_str": self.backend.beauty_size(rcu.get("install_size", 0)),
                "to_upgrade": rcu.get("to_upgrade", []),
                "to_keep": rcu.get("to_keep", []),
            }
        return {
            "download_size": 0,
            "install_size": 0,
            "download_size_str": "0 B",
            "install_size_str": "0 B",
            "to_upgrade": [],
            "to_keep": [],
        }

    def get_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return repositories/mirrors from system configuration."""
        if hasattr(self.backend, "get_sources"):
            return self.backend.get_sources()
        return {}

    def get_orphans(self) -> List[str]:
        """Return orphaned packages eligible for autoremove."""
        if hasattr(self.backend, "autoremovable"):
            return self.backend.autoremovable()
        return []

    def get_package_details(self, pkg_name: str) -> Dict[str, Any]:
        """Fetches metadata, dependency details, and changelog for a package."""
        details: Dict[str, Any] = {
            "name": pkg_name,
            "version": "",
            "description": "",
            "url": "",
            "repository": "",
            "download_size": "",
            "depends": [],
            "changelog": "",
            "requires_reboot": self.requires_reboot(pkg_name),
        }
        if hasattr(self.backend, "_query_pacman_si"):
            info = self.backend._query_pacman_si(pkg_name)
            details["version"] = info.get("version", "")
            details["description"] = info.get("description", "")
            details["url"] = info.get("url", "")
            details["repository"] = info.get("repository", "")
            details["download_size"] = self.backend.size(pkg_name)
            details["depends"] = info.get("depends", [])
            try:
                res = subprocess.run(["pacman", "-Qc", pkg_name], capture_output=True, text=True, timeout=3)
                if res.returncode == 0 and res.stdout.strip():
                    details["changelog"] = res.stdout.strip()
            except Exception:
                pass
        else:
            try:
                details["version"] = getattr(self.backend, "candidate_version", lambda x: "")(pkg_name)
                details["description"] = getattr(self.backend, "summary", lambda x: "")(pkg_name)
                details["download_size"] = getattr(self.backend, "size", lambda x: "")(pkg_name)
                res = subprocess.run(["apt-get", "changelog", "--print-uris", pkg_name], capture_output=True, text=True, timeout=3)
                if res.returncode == 0 and res.stdout.strip():
                    details["changelog"] = res.stdout.strip()
            except Exception:
                pass
        return details

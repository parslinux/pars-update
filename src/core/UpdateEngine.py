#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core update engine for Pars Update.
Decoupled from UI, handles package manager operations for both Arch Linux and Debian/Pars.
"""

import logging
import os
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network monitoring abstraction for Pars Update.
Uses GIO / NetworkManager to detect connectivity and metered (mobile/hotspot) connections.
"""

import logging
from typing import Callable, List, Optional

try:
    import gi
    gi.require_version("Gio", "2.0")
    from gi.repository import Gio
    HAVE_GIO = True
except (ImportError, ValueError):
    Gio = None
    HAVE_GIO = False

logger = logging.getLogger("pars-update.network")


class NetworkMonitor:
    """Monitors system network connectivity and metered connection states."""

    def __init__(self) -> None:
        self._monitor: Optional[Gio.NetworkMonitor] = None
        self._listeners: List[Callable[[bool, bool], None]] = []
        if HAVE_GIO and Gio:
            try:
                self._monitor = Gio.NetworkMonitor.get_default()
                if self._monitor:
                    self._monitor.connect("network-changed", self._on_network_changed)
            except Exception as e:
                logger.warning("Could not initialize Gio.NetworkMonitor: %s", e)

    @property
    def is_connected(self) -> bool:
        """Returns True if there is an active network connection with internet access."""
        if not self._monitor:
            return True
        try:
            return bool(self._monitor.get_network_available())
        except Exception:
            return True

    @property
    def is_metered(self) -> bool:
        """Returns True if connection is metered (e.g. mobile hotspot / LTE / cellular data)."""
        if not self._monitor:
            return False
        try:
            return bool(self._monitor.get_network_metered())
        except Exception:
            return False

    @property
    def connectivity(self) -> int:
        """Returns Gio.NetworkConnectivity value (e.g. 4 for FULL, 1 for LOCAL, 0 for NONE)."""
        if not self._monitor:
            return 4
        try:
            return int(self._monitor.get_connectivity())
        except Exception:
            return 4

    def add_listener(self, callback: Callable[[bool, bool], None]) -> None:
        """Register a callback for network changes: callback(is_connected, is_metered)."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[bool, bool], None]) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _on_network_changed(self, monitor: Gio.NetworkMonitor, available: bool) -> None:
        connected = self.is_connected
        metered = self.is_metered
        logger.debug("Network changed: connected=%s, metered=%s", connected, metered)
        for cb in list(self._listeners):
            try:
                cb(connected, metered)
            except Exception as e:
                logger.error("Error in network change callback: %s", e)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration manager for Pars Update.
Manages user and system settings (intervals, autostart, notifications).
"""

import os
import sys
import time
from typing import Any, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from UserSettings import UserSettings
from SystemSettings import SystemSettings


class ConfigManager:
    """Unified wrapper around user settings and system configurations."""

    def __init__(self) -> None:
        self.user = UserSettings()
        self.system = SystemSettings()

    @property
    def interval(self) -> int:
        if self.system.config_update_interval is not None:
            return self.system.config_update_interval
        return self.user.config_update_interval

    @interval.setter
    def interval(self, val: int) -> None:
        self.user.config_update_interval = val
        self._save()

    @property
    def last_update(self) -> int:
        return self.user.config_update_lastupdate

    @last_update.setter
    def last_update(self, val: int) -> None:
        self.user.config_update_lastupdate = val
        self._save()

    @property
    def autostart(self) -> bool:
        return bool(self.user.config_autostart)

    @autostart.setter
    def autostart(self, val: bool) -> None:
        self.user.config_autostart = val
        self._save()

    @property
    def notifications(self) -> bool:
        return bool(self.user.config_notifications)

    @notifications.setter
    def notifications(self, val: bool) -> None:
        self.user.config_notifications = val
        self._save()

    @property
    def selectable(self) -> bool:
        return bool(self.user.config_update_selectable)

    @selectable.setter
    def selectable(self, val: bool) -> None:
        self.user.config_update_selectable = val
        self._save()

    def record_update_now(self) -> None:
        """Record current timestamp as last update check time."""
        now = int(time.time())
        self.last_update = now

    def _save(self) -> None:
        self.user.writeConfig(
            self.user.config_update_interval,
            self.user.config_update_lastupdate,
            self.user.config_update_selectable,
            self.user.config_autostart,
            self.user.config_notifications,
        )

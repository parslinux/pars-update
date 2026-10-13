#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Desktop notification manager for Pars Update.
Uses libnotify for system-wide desktop notifications.
"""

import logging
import os
from typing import Callable, List, Optional

import gi

try:
    gi.require_version("Notify", "0.7")
    from gi.repository import Notify
    HAVE_NOTIFY = True
except Exception:
    HAVE_NOTIFY = False

logger = logging.getLogger("pars-update-notify")


class NotificationManager:
    """Manages system notifications for available updates and completion status."""

    def __init__(self, app_name: str = "Pars Update") -> None:
        self.app_name = app_name
        self._initialized = False
        if HAVE_NOTIFY:
            try:
                Notify.init(self.app_name)
                self._initialized = True
            except Exception as e:
                logger.warning("Failed to init Notify: %s", e)

    def notify_updates_available(self, count: int, packages: Optional[List[str]] = None,
                                 on_update_clicked: Optional[Callable[[], None]] = None) -> None:
        """Show notification that updates are available."""
        if not self._initialized:
            return

        title = f"{count} Yeni Güncelleme Mevcut" if count > 1 else "1 Yeni Güncelleme Mevcut"
        body = "Sisteminiz ve kurulu uygulamalarınız için yeni güncellemeler hazır."
        if packages and len(packages) <= 5:
            body += "\nPaketler: " + ", ".join(packages)
        elif packages:
            body += f"\n{packages[0]}, {packages[1]}, {packages[2]} ve {len(packages) - 3} diğer paket."

        try:
            notification = Notify.Notification.new(title, body, "pars-update")
            notification.set_urgency(Notify.Urgency.NORMAL)
            notification.show()
        except Exception as e:
            logger.debug("Failed to show notification: %s", e)

    def notify_completed(self) -> None:
        """Show notification that system upgrade completed successfully."""
        if not self._initialized:
            return
        try:
            notification = Notify.Notification.new(
                "Güncelleme Tamamlandı",
                "Sisteminiz başarıyla en güncel sürüme yükseltildi.",
                "pars-update-uptodate"
            )
            notification.set_urgency(Notify.Urgency.LOW)
            notification.show()
        except Exception as e:
            logger.debug("Failed to show completed notification: %s", e)

    def notify_error(self, message: str) -> None:
        """Show notification for package manager errors."""
        if not self._initialized:
            return
        try:
            notification = Notify.Notification.new(
                "Güncelleme Hatası",
                message or "İşlem sırasında bir hata oluştu.",
                "pars-update-error-symbolic"
            )
            notification.set_urgency(Notify.Urgency.CRITICAL)
            notification.show()
        except Exception as e:
            logger.debug("Failed to show error notification: %s", e)

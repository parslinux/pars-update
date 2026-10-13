#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal runner for GTK4 VTE terminal.
Eliminates code duplication across all privileged execution commands.
"""

import logging
import os
from typing import Any, Callable, List, Optional

import gi

try:
    gi.require_version("Vte", "3.91")
    from gi.repository import Vte, GLib, Gio
    HAVE_VTE4 = True
except Exception:
    HAVE_VTE4 = False

logger = logging.getLogger("pars-update-vte")


class TerminalRunner:
    """Manages VTE terminal process spawning and completion callbacks in GTK4."""

    def __init__(self, terminal: Any = None) -> None:
        self.terminal = terminal
        self.pty = None
        self._on_done: Optional[Callable[[int], None]] = None

    def spawn(self, terminal: Any, command: List[str], on_done: Optional[Callable[[int], None]] = None) -> bool:
        """Spawn command in the specified GTK4 Vte.Terminal."""
        self.terminal = terminal
        self._on_done = on_done

        if not HAVE_VTE4:
            logger.warning("VTE 3.91 is not available for GTK4.")
            return False
        if not terminal:
            logger.debug("No terminal widget provided to TerminalRunner.")
            return False

        try:
            pty = Vte.Pty.new_sync(Vte.PtyFlags.DEFAULT, None)
            self.pty = pty
            terminal.set_pty(pty)

            terminal.connect("child-exited", self._on_child_exited)

            # Spawn async in GTK4
            terminal.spawn_async(
                Vte.PtyFlags.DEFAULT,
                os.environ.get("HOME", "/tmp"),
                command,
                None,  # envv
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,  # child_setup
                None,  # child_setup_data
                -1,    # timeout
                None,  # cancellable
                self._on_spawn_ready,
                None   # user_data
            )
            return True
        except Exception as e:
            logger.error("Failed to spawn process in VTE: %s", e)
            return False

    def _on_spawn_ready(self, terminal: Any, pid: int, error: Any, user_data: Any) -> None:
        if error:
            logger.error("Spawn error: %s", error)
        else:
            logger.debug("Spawned PID: %d", pid)

    def _on_child_exited(self, terminal: Any, status: int) -> None:
        logger.info("Terminal process exited with status: %d", status)
        if self._on_done:
            self._on_done(status)

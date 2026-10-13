#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern GTK4 / Libadwaita Main Window for Pars Update.
Replaces the 2700-line legacy GTK3 MainWindow with clean Libadwaita architecture.
"""

from datetime import datetime
import logging
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk

try:
    gi.require_version("Vte", "3.91")
    from gi.repository import Vte
    HAVE_VTE = True
except Exception:
    HAVE_VTE = False

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ConfigManager import ConfigManager
from core.NotificationManager import NotificationManager
from core.TerminalRunner import TerminalRunner
from core.UpdateEngine import UpdateEngine
from ui.PreferencesAdw import PreferencesAdw

logger = logging.getLogger("pars-update-ui")


class MainWindowAdw(Adw.ApplicationWindow):
    """Modern GTK4 / Libadwaita Main Window for Pars Update."""

    def __init__(self, application: Adw.Application) -> None:
        super().__init__(application=application)
        self.set_title("Pars Update")
        self.set_default_size(680, 580)
        self.set_size_request(450, 400)

        self.engine = UpdateEngine()
        self.config = ConfigManager()
        self.notifications = NotificationManager()
        self.terminal_runner = TerminalRunner()

        self.current_updates: List[Dict[str, Any]] = []
        self.unselected_packages: set = set()
        self.upgrade_in_progress = False

        self._load_custom_css()
        self._build_ui()
        self._setup_autoupdate_timer()

        # Trigger initial check
        GLib.idle_add(self.refresh_updates)

    def _load_custom_css(self) -> None:
        css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "data", "style.css")
        if os.path.exists(css_path):
            try:
                provider = Gtk.CssProvider()
                provider.load_from_path(css_path)
                display = Gdk.Display.get_default()
                if display:
                    Gtk.StyleProvider.add_provider_for_display(
                        display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                    )
            except Exception as e:
                logger.debug("Failed to load CSS: %s", e)

    def _build_ui(self) -> None:
        self.toolbar_view = Adw.ToolbarView()
        self.set_content(self.toolbar_view)

        # HeaderBar
        self.header_bar = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(self.header_bar)

        # Title Widget
        title_widget = Adw.WindowTitle(title="Pars Update", subtitle="Sistem Güncelleme Yöneticisi")
        self.header_bar.set_title_widget(title_widget)

        # Refresh button
        self.refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic")
        self.refresh_btn.set_tooltip_text("Güncellemeleri Denetle")
        self.refresh_btn.connect("clicked", lambda b: self.refresh_updates())
        self.header_bar.pack_start(self.refresh_btn)

        # Menu Button
        self.menu_btn = Gtk.MenuButton(icon_name="open-menu-symbolic")
        menu = Gio.Menu()
        menu.append("Ayarlar", "win.preferences")
        menu.append("Hakkında", "win.about")
        self.menu_btn.set_menu_model(menu)
        self.header_bar.pack_end(self.menu_btn)

        self._setup_actions()

        # Toast Overlay
        self.toast_overlay = Adw.ToastOverlay()
        self.toolbar_view.set_content(self.toast_overlay)

        # View Stack for Pages
        self.stack = Adw.ViewStack()
        self.toast_overlay.set_child(self.stack)

        self._build_page_uptodate()
        self._build_page_checking()
        self._build_page_updates()
        self._build_page_terminal()
        self._build_page_error()

    def _setup_actions(self) -> None:
        action_pref = Gio.SimpleAction.new("preferences", None)
        action_pref.connect("activate", lambda a, p: self._open_preferences())
        self.add_action(action_pref)

        action_about = Gio.SimpleAction.new("about", None)
        action_about.connect("activate", lambda a, p: self._open_about())
        self.add_action(action_about)

    def _build_page_uptodate(self) -> None:
        self.page_uptodate = Adw.StatusPage()
        self.page_uptodate.set_title("Sisteminiz Güncel")
        self.page_uptodate.set_description("Tüm paketler ve güvenlik yamaları en son sürümde.")

        svg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "data", "pars-update-uptodate.svg")
        if os.path.exists(svg_path):
            icon_file = Gio.File.new_for_path(svg_path)
            self.page_uptodate.set_paintable(Gtk.IconPaintable.new_for_file(icon_file, 128, 1))
        else:
            self.page_uptodate.set_icon_name("software-update-available-symbolic")

        btn = Gtk.Button(label="Yeniden Denetle")
        btn.add_css_class("pill")
        btn.add_css_class("suggested-action")
        btn.connect("clicked", lambda b: self.refresh_updates())
        self.page_uptodate.set_child(btn)

        self.stack.add_named(self.page_uptodate, "uptodate")

    def _build_page_checking(self) -> None:
        self.page_checking = Adw.StatusPage()
        self.page_checking.set_title("Güncellemeler Denetleniyor...")
        self.page_checking.set_description("Paket depoları sorgulanıyor, lütfen bekleyin.")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_halign(Gtk.Align.CENTER)
        spinner = Gtk.Spinner()
        spinner.set_size_request(48, 48)
        spinner.start()
        box.append(spinner)

        self.page_checking.set_child(box)
        self.stack.add_named(self.page_checking, "checking")

    def _build_page_updates(self) -> None:
        scrolled = Gtk.ScrolledWindow()
        clamp = Adw.Clamp()
        clamp.set_maximum_size(720)
        scrolled.set_child(clamp)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)
        clamp.set_child(main_box)

        # Header Info Card
        self.updates_group = Adw.PreferencesGroup()
        self.updates_group.set_title("Mevcut Güncellemeler")
        self.updates_summary_label = Gtk.Label(label="")
        self.updates_summary_label.set_halign(Gtk.Align.START)
        self.updates_summary_label.add_css_class("dim-label")
        self.updates_group.set_header_suffix(self.updates_summary_label)

        main_box.append(self.updates_group)

        # Bottom Action Bar
        bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        bottom_box.set_margin_top(8)

        self.size_info_label = Gtk.Label(label="")
        self.size_info_label.set_hexpand(True)
        self.size_info_label.set_halign(Gtk.Align.START)
        bottom_box.append(self.size_info_label)

        self.upgrade_btn = Gtk.Button(label="Sistemi Güncelle")
        self.upgrade_btn.add_css_class("suggested-action")
        self.upgrade_btn.add_css_class("pill")
        self.upgrade_btn.connect("clicked", lambda b: self.start_upgrade())
        bottom_box.append(self.upgrade_btn)

        main_box.append(bottom_box)
        self.stack.add_named(scrolled, "updates")

    def _build_page_terminal(self) -> None:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        # Header info
        term_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.term_status_label = Gtk.Label(label="Güncellemeler yükleniyor...")
        self.term_status_label.set_hexpand(True)
        self.term_status_label.set_halign(Gtk.Align.START)
        self.term_status_label.add_css_class("title-4")
        term_header.append(self.term_status_label)

        self.term_progress = Gtk.ProgressBar()
        self.term_progress.set_pulse_step(0.1)

        box.append(term_header)
        box.append(self.term_progress)

        # VTE Terminal Container
        term_sw = Gtk.ScrolledWindow()
        term_sw.set_vexpand(True)
        term_sw.set_hexpand(True)

        if HAVE_VTE:
            self.vte = Vte.Terminal()
            self.vte.set_scrollback_lines(5000)
            self.vte.set_cursor_blink_mode(Vte.CursorBlinkMode.OFF)
            term_sw.set_child(self.vte)
        else:
            self.vte = None
            lbl = Gtk.Label(label="VTE Terminal bileşeni yüklenemedi.")
            term_sw.set_child(lbl)

        box.append(term_sw)

        # Bottom Bar
        self.term_bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.term_done_btn = Gtk.Button(label="Tamamlandı")
        self.term_done_btn.add_css_class("suggested-action")
        self.term_done_btn.set_visible(False)
        self.term_done_btn.connect("clicked", lambda b: self._on_terminal_finished_clicked())
        self.term_bottom.append(self.term_done_btn)

        box.append(self.term_bottom)
        self.stack.add_named(box, "terminal")

    def _build_page_error(self) -> None:
        self.page_error = Adw.StatusPage()
        self.page_error.set_title("İşlem Tamamlanamadı")
        self.page_error.set_description("Paket yöneticisi meşgul veya kilitli.")

        svg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "data", "pars-update-cantconnect.svg")
        if os.path.exists(svg_path):
            icon_file = Gio.File.new_for_path(svg_path)
            self.page_error.set_paintable(Gtk.IconPaintable.new_for_file(icon_file, 128, 1))
        else:
            self.page_error.set_icon_name("dialog-error-symbolic")

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)

        retry_btn = Gtk.Button(label="Tekrar Dene")
        retry_btn.add_css_class("suggested-action")
        retry_btn.connect("clicked", lambda b: self.refresh_updates())
        btn_box.append(retry_btn)

        fix_btn = Gtk.Button(label="Kilidi Kaldır (Fix)")
        fix_btn.add_css_class("destructive-action")
        fix_btn.connect("clicked", lambda b: self._on_fix_lock_clicked())
        btn_box.append(fix_btn)

        self.page_error.set_child(btn_box)
        self.stack.add_named(self.page_error, "error")

    def refresh_updates(self) -> None:
        """Triggers asynchronous update check and shows spinner page."""
        if self.upgrade_in_progress:
            return

        self.stack.set_visible_child_name("checking")
        self.refresh_btn.set_sensitive(False)

        # Check if locked first
        locked, msg = self.engine.is_locked()
        if locked:
            self.page_error.set_description(msg or "Paket yöneticisi başka bir işlem tarafından kilitlenmiş.")
            self.stack.set_visible_child_name("error")
            self.refresh_btn.set_sensitive(True)
            return

        self.engine.check_updates_async(self._on_check_completed)

    def _on_check_completed(self, updates: List[Dict[str, Any]], error: Optional[Exception]) -> None:
        self.refresh_btn.set_sensitive(True)

        if error:
            self.page_error.set_description(str(error))
            self.stack.set_visible_child_name("error")
            return

        self.current_updates = updates
        self.unselected_packages.clear()
        self.config.record_update_now()

        if not updates:
            now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
            self.page_uptodate.set_description(f"Tüm paketler ve güvenlik yamaları en son sürümde.\nSon Kontrol: {now_str}")
            self.stack.set_visible_child_name("uptodate")
        else:
            self._populate_updates_view(updates)
            self.stack.set_visible_child_name("updates")
            if self.config.notifications:
                self.notifications.notify_updates_available(len(updates), [u["name"] for u in updates[:5]])

    def _populate_updates_view(self, updates: List[Dict[str, Any]]) -> None:
        # Clear existing rows
        # Adw.PreferencesGroup doesn't have remove_all, so we rebuild group if needed
        # Or remove child rows
        while True:
            first_child = self.updates_group.get_first_child()
            if not first_child:
                break
            self.updates_group.remove(first_child)

        self.updates_summary_label.set_text(f"{len(updates)} paket")

        for u in updates:
            pkg_name = u["name"]
            row = Adw.ActionRow()
            row.set_title(pkg_name)
            ver_text = f"{u['old_version']} ➔ {u['new_version']}" if u.get("old_version") else u.get("new_version", "")
            row.set_subtitle(ver_text)

            # Checkbox
            check = Gtk.CheckButton()
            check.set_active(pkg_name not in self.unselected_packages)
            check.set_valign(Gtk.Align.CENTER)
            check.connect("toggled", self._on_package_toggle, pkg_name)
            row.add_prefix(check)

            # Size badge
            size_badge = Gtk.Label(label=u.get("size_str", ""))
            size_badge.add_css_class("badge-ready")
            size_badge.set_valign(Gtk.Align.CENTER)
            row.add_suffix(size_badge)

            self.updates_group.add(row)

        self._update_size_summary()

    def _on_package_toggle(self, check: Gtk.CheckButton, pkg_name: str) -> None:
        if check.get_active():
            self.unselected_packages.discard(pkg_name)
        else:
            self.unselected_packages.add(pkg_name)
        self._update_size_summary()

    def _update_size_summary(self) -> None:
        sizes = self.engine.calculate_sizes(keep_list=list(self.unselected_packages))
        d_str = sizes.get("download_size_str", "0 B")
        count = len(self.current_updates) - len(self.unselected_packages)
        self.size_info_label.set_text(f"Seçilen: {count} paket  •  İndirme Boyutu: {d_str}")
        self.upgrade_btn.set_sensitive(count > 0)

    def start_upgrade(self) -> None:
        """Launches privileged upgrade inside the VTE terminal."""
        if not HAVE_VTE or not self.vte:
            self._show_toast("VTE Terminal bulunamadığı için yükseltme başlatılamadı.")
            return

        self.upgrade_in_progress = True
        self.refresh_btn.set_sensitive(False)
        self.term_done_btn.set_visible(False)
        self.term_progress.pulse()
        self.term_status_label.set_text("Güncellemeler kuruluyor...")
        self.stack.set_visible_child_name("terminal")

        # Prepare SysActions command
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys_actions_path = os.path.join(script_dir, "SysActions.py")

        keeps_str = " ".join(self.unselected_packages)
        cmd = ["/usr/bin/pkexec", sys_actions_path, "upgrade", "yes", "new", keeps_str]

        self.terminal_runner.spawn(self.vte, cmd, self._on_upgrade_done)

    def _on_upgrade_done(self, status: int) -> None:
        self.upgrade_in_progress = False
        self.refresh_btn.set_sensitive(True)
        self.term_done_btn.set_visible(True)

        if status == 0:
            self.term_status_label.set_text("✓ Güncelleme başarıyla tamamlandı!")
            self.notifications.notify_completed()
            self._show_toast("Tüm güncellemeler başarıyla kuruldu.")
        else:
            self.term_status_label.set_text(f"✗ İşlem tamamlanamadı (Çıkış Kodu: {status})")
            self._show_toast("Güncelleme işlemi sırasında bir sorun oluştu.")

    def _on_terminal_finished_clicked(self) -> None:
        self.refresh_updates()

    def _on_fix_lock_clicked(self) -> None:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cmd = ["/usr/bin/pkexec", os.path.join(script_dir, "SysActions.py"), "dpkgconfigure"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            self._show_toast("Kilit temizleme işlemi çalıştırıldı.")
        except Exception as e:
            self._show_toast(f"Hata: {e}")
        self.refresh_updates()

    def _open_preferences(self) -> None:
        pref_win = PreferencesAdw(self, self.config, self.engine)
        pref_win.present()

    def _open_about(self) -> None:
        about = Adw.AboutDialog()
        about.set_application_name("Pars Update")
        about.set_application_icon("pars-update")
        about.set_version("1.4.4")
        about.set_developer_name("Pars Linux Geliştiricileri")
        about.set_developers(["Pars Linux Team <dev@parslinux.org>"])
        about.set_website("https://github.com/parslinux/pars-update")
        about.set_issue_url("https://github.com/parslinux/pars-update/issues")
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_copyright("© 2026 Pars Linux")
        about.present(self)

    def _setup_autoupdate_timer(self) -> None:
        interval = self.config.interval
        if interval > 0:
            GLib.timeout_add_seconds(interval, self._timer_callback)

    def _timer_callback(self) -> bool:
        if not self.upgrade_in_progress:
            self.engine.check_updates_async(self._on_check_completed)
        return True

    def handle_args(self, args: Dict[str, Any]) -> None:
        """Handles CLI arguments like --page or --check."""
        page = args.get("page")
        if page:
            if page in ("settings", "preferences", "ayarlar"):
                self._open_preferences()
            elif page in ("updates", "checking", "uptodate", "terminal", "error"):
                self.stack.set_visible_child_name(page)
            elif page == "updateinfo":
                if self.current_updates:
                    self.stack.set_visible_child_name("updates")
                else:
                    self.stack.set_visible_child_name("uptodate")

    def _show_toast(self, message: str) -> None:
        toast = Adw.Toast.new(message)
        self.toast_overlay.add_toast(toast)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern Libadwaita Preferences Window for Pars Update.
Provides general settings, mirror/repository toggles, and cache maintenance.
"""

import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, Gtk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ConfigManager import ConfigManager
from core.UpdateEngine import UpdateEngine


class PreferencesAdw(Adw.PreferencesWindow):
    """Modern Preferences Window using Libadwaita widgets."""

    def __init__(self, parent_window: Any, config: ConfigManager, engine: UpdateEngine) -> None:
        super().__init__(transient_for=parent_window, modal=True)
        self.set_title("Ayarlar — Pars Update")
        self.set_default_size(580, 500)

        self.config = config
        self.engine = engine

        self._build_general_page()
        self._build_sources_page()
        self._build_maintenance_page()

    def _build_general_page(self) -> None:
        page = Adw.PreferencesPage()
        page.set_title("Genel")
        page.set_icon_name("preferences-system-symbolic")

        # Automatic checks group
        check_group = Adw.PreferencesGroup()
        check_group.set_title("Güncelleme Denetimi")
        check_group.set_description("Sistemin güncellemeleri hangi sıklıkla denetleyeceğini ayarlayın.")

        # Interval ComboRow
        self.interval_row = Adw.ComboRow()
        self.interval_row.set_title("Otomatik Kontrol Sıklığı")
        self.interval_row.set_subtitle("Arka planda yeni sürümlerin aranma aralığı")

        intervals = ["Her Gün", "Her Hafta", "Asla (Yalnızca Elle)"]
        interval_values = [86400, 604800, -1]
        model = Gtk.StringList.new(intervals)
        self.interval_row.set_model(model)

        curr_interval = self.config.interval
        if curr_interval == 604800:
            self.interval_row.set_selected(1)
        elif curr_interval == -1:
            self.interval_row.set_selected(2)
        else:
            self.interval_row.set_selected(0)

        self.interval_row.connect("notify::selected", self._on_interval_changed, interval_values)
        check_group.add(self.interval_row)

        # Autostart switch
        self.autostart_row = Adw.SwitchRow()
        self.autostart_row.set_title("Açılışta Otomatik Başlat")
        self.autostart_row.set_subtitle("Oturum açıldığında güncellemeleri arka planda kontrol et")
        self.autostart_row.set_active(self.config.autostart)
        self.autostart_row.connect("notify::active", lambda row, ps: setattr(self.config, "autostart", row.get_active()))
        check_group.add(self.autostart_row)

        # Notifications switch
        self.notif_row = Adw.SwitchRow()
        self.notif_row.set_title("Masaüstü Bildirimleri")
        self.notif_row.set_subtitle("Yeni paketler bulunduğunda bildirim göster")
        self.notif_row.set_active(self.config.notifications)
        self.notif_row.connect("notify::active", lambda row, ps: setattr(self.config, "notifications", row.get_active()))
        check_group.add(self.notif_row)

        # Metered network switch
        self.metered_row = Adw.SwitchRow()
        self.metered_row.set_title("Kotalı Ağlarda İndirmeyi Duraklat")
        self.metered_row.set_subtitle("Mobil erişim noktası veya kotalı ağlarda mobil veriyi korur")
        self.metered_row.set_active(self.config.pause_on_metered)
        self.metered_row.connect("notify::active", lambda row, ps: setattr(self.config, "pause_on_metered", row.get_active()))
        check_group.add(self.metered_row)

        page.add(check_group)
        self.add(page)

    def _on_interval_changed(self, row: Adw.ComboRow, pspec: Any, values: List[int]) -> None:
        idx = row.get_selected()
        if 0 <= idx < len(values):
            self.config.interval = values[idx]

    def _build_sources_page(self) -> None:
        page = Adw.PreferencesPage()
        page.set_title("Depolar ve Aynalar")
        page.set_icon_name("network-server-symbolic")

        group = Adw.PreferencesGroup()
        backend_name = "Arch Linux (Pacman Aynaları)" if self.engine.backend_name == "pacman" else "Debian / Pars Depoları"
        group.set_title(backend_name)
        group.set_description("Sistem paketlerinin indirildiği aktif yansı sunucuları.")

        sources = self.engine.get_sources()
        count = 0
        for uri, sublist in sources.items():
            for sub in sublist:
                if count >= 30:  # Limit display for ultra-long mirrorlists to keep UI snappy
                    break
                row = Adw.ActionRow()
                row.set_title(sub.get("uri", uri))
                row.set_subtitle(sub.get("file", ""))

                switch = Gtk.Switch()
                switch.set_active(not sub.get("disabled", False))
                switch.set_valign(Gtk.Align.CENTER)
                switch.connect("state-set", self._on_source_switch, sub)
                row.add_suffix(switch)
                group.add(row)
                count += 1

        if count == 0:
            empty_row = Adw.ActionRow()
            empty_row.set_title("Yapılandırılmış depo dosyası bulunamadı")
            group.add(empty_row)

        page.add(group)
        self.add(page)

    def _on_source_switch(self, switch: Gtk.Switch, state: bool, sub_data: Dict[str, Any]) -> bool:
        cmd = [
            "/usr/bin/pkexec",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "AptSourceActions.py"),
            "setsourcestate",
            "1" if state else "0",
            sub_data.get("line", ""),
            sub_data.get("file", "")
        ]
        try:
            subprocess.Popen(cmd)
        except Exception as e:
            print("Error toggling mirror state:", e)
        return False

    def _build_maintenance_page(self) -> None:
        page = Adw.PreferencesPage()
        page.set_title("Bakım")
        page.set_icon_name("user-trash-symbolic")

        group = Adw.PreferencesGroup()
        group.set_title("Sistem Önbellek ve Artık Temizliği")
        group.set_description("Diskte yer açmak için indirilmiş paket arşivlerini ve yetim bağımlılıkları temizleyin.")

        # Cache clean row
        cache_row = Adw.ActionRow()
        cache_row.set_title("Paket Arşiv Önbelleğini Temizle")
        cache_desc = "İndirilmiş .pkg.tar.zst arşivlerini siler (pacman -Sc)" if self.engine.backend_name == "pacman" else "İndirilmiş .deb dosyalarını siler (apt clean)"
        cache_row.set_subtitle(cache_desc)

        clean_btn = Gtk.Button(label="Temizle")
        clean_btn.set_valign(Gtk.Align.CENTER)
        clean_btn.add_css_class("destructive-action")
        clean_btn.connect("clicked", self._on_clean_cache_clicked)
        cache_row.add_suffix(clean_btn)
        group.add(cache_row)

        # Orphans remove row
        orphans_row = Adw.ActionRow()
        orphans_row.set_title("Yetim (Gereksiz) Paketleri Kaldır")
        orphans_row.set_subtitle("Başka hiçbir paketin ihtiyaç duymadığı terk edilmiş bağımlılıkları temizler")

        orphans_btn = Gtk.Button(label="Kaldır")
        orphans_btn.set_valign(Gtk.Align.CENTER)
        orphans_btn.connect("clicked", self._on_remove_orphans_clicked)
        orphans_row.add_suffix(orphans_btn)
        group.add(orphans_row)

        page.add(group)
        self.add(page)

    def _on_clean_cache_clicked(self, btn: Gtk.Button) -> None:
        cmd = [
            "/usr/bin/pkexec",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SysActions.py"),
            "aptclear", "1", "0", "0"
        ]
        subprocess.Popen(cmd)

    def _on_remove_orphans_clicked(self, btn: Gtk.Button) -> None:
        cmd = [
            "/usr/bin/pkexec",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SysActions.py"),
            "removeauto"
        ]
        subprocess.Popen(cmd)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package manager detection and Arch Linux (pacman) / Debian (apt) backend abstraction
for Pars Update.
"""

import locale
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

try:
    from gi.repository import Gio, GLib
except ImportError:
    Gio = None
    GLib = None


def get_distro_info():
    """
    Safely retrieves distribution information without crashing on rolling releases
    or missing python3-distro package.
    """
    distro_info = {
        "id": "unknown",
        "name": "Linux",
        "version": "",
        "major_version": 0,
        "codename": "",
        "like": "",
        "package_manager": "apt"
    }

    # First attempt: parse /etc/os-release
    os_release = "/etc/os-release"
    if os.path.exists(os_release):
        try:
            with open(os_release, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line:
                        k, v = line.split("=", 1)
                        v = v.strip('"\'')
                        if k == "ID":
                            distro_info["id"] = v.lower()
                        elif k == "NAME":
                            distro_info["name"] = v
                        elif k == "VERSION_ID":
                            distro_info["version"] = v
                            digits = re.findall(r"\d+", v)
                            if digits:
                                distro_info["major_version"] = int(digits[0])
                        elif k == "VERSION_CODENAME":
                            distro_info["codename"] = v.lower()
                        elif k == "ID_LIKE":
                            distro_info["like"] = v.lower()
        except Exception as e:
            print("Error parsing /etc/os-release: {}".format(e))

    # Optional: try python-distro module if available
    try:
        import distro
        dist_id = distro.id()
        if dist_id:
            distro_info["id"] = dist_id.lower()
        if distro.name():
            distro_info["name"] = distro.name()
        maj = distro.major_version()
        if maj and maj.isdigit():
            distro_info["major_version"] = int(maj)
        cod = distro.codename()
        if cod:
            distro_info["codename"] = cod.lower()
        lik = distro.like()
        if lik:
            distro_info["like"] = lik.lower()
    except Exception:
        pass

    # Detect package manager
    distro_id = distro_info["id"]
    distro_like = distro_info["like"]

    if distro_id in ["arch", "manjaro", "endeavouros", "garuda", "artix"] or "arch" in distro_like.split():
        distro_info["package_manager"] = "pacman"
    elif shutil.which("pacman") and not shutil.which("apt"):
        distro_info["package_manager"] = "pacman"
    elif shutil.which("pacman") and os.path.exists("/etc/arch-release"):
        distro_info["package_manager"] = "pacman"
    else:
        distro_info["package_manager"] = "apt"

    return distro_info


def get_package_manager():
    """Returns detected package manager ('pacman' or 'apt')."""
    return get_distro_info()["package_manager"]


def parse_pacman_size_str(size_str):
    """Converts pacman size string (e.g. '528.93 KiB', '12.40 MiB') into integer bytes."""
    if not size_str or not isinstance(size_str, str):
        return 0
    parts = size_str.strip().split()
    if not parts:
        return 0
    try:
        num = float(parts[0].replace(",", "."))
    except ValueError:
        return 0
    unit = parts[1].upper() if len(parts) > 1 else "B"
    multipliers = {
        "B": 1,
        "KIB": 1024,
        "KB": 1000,
        "MIB": 1024 * 1024,
        "MB": 1000 * 1000,
        "GIB": 1024 * 1024 * 1024,
        "GB": 1000 * 1000 * 1000,
    }
    return int(num * multipliers.get(unit, 1))


class PacmanBackend(object):
    """
    Native Arch Linux backend using pacman, checkupdates and vercmp.
    """
    def __init__(self):
        self.apps = []
        self.secs = []
        self.sections = []
        self.update_cache_error_msg = ""
        self._pkg_info_cache = {}
        self._upgradable_cache = {}

    def updatecache(self):
        """Refreshes available update cache."""
        self._pkg_info_cache.clear()
        self._upgradable_cache.clear()
        if os.path.exists("/var/lib/pacman/db.lck"):
            self.update_cache_error_msg = "Pacman database is currently locked (/var/lib/pacman/db.lck)."
            return False
        return True

    def control_dpkg_interrupt(self):
        """Returns True if database is locked/interrupted."""
        return os.path.exists("/var/lib/pacman/db.lck")

    def control_lock(self):
        """Checks pacman db lock."""
        lock_path = "/var/lib/pacman/db.lck"
        if os.path.exists(lock_path):
            msg = "pacman database lock file exists (/var/lib/pacman/db.lck)"
            return False, msg
        return True, ""

    def _query_pacman_si(self, packagename):
        """Queries pacman -Si for a package with in-memory caching."""
        if packagename in self._pkg_info_cache:
            return self._pkg_info_cache[packagename]

        info = {
            "name": packagename,
            "version": "",
            "description": "",
            "architecture": "",
            "url": "",
            "download_size": 0,
            "installed_size": 0,
            "packager": "",
            "repository": "",
            "depends": [],
        }

        # Try pacman -Si first (sync repository)
        cmd = ["pacman", "-Si", packagename]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env={**os.environ, "LC_ALL": "C"})
        if res.returncode != 0:
            # Fallback to pacman -Qi (installed package)
            cmd = ["pacman", "-Qi", packagename]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 env={**os.environ, "LC_ALL": "C"})

        if res.returncode == 0:
            for line in res.stdout.decode("utf-8", errors="ignore").splitlines():
                if ":" not in line:
                    continue
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip()
                if k == "Version":
                    info["version"] = v
                elif k == "Description":
                    info["description"] = v
                elif k == "Architecture":
                    info["architecture"] = v
                elif k == "URL":
                    info["url"] = v
                elif k == "Download Size":
                    info["download_size"] = parse_pacman_size_str(v)
                elif k == "Installed Size":
                    info["installed_size"] = parse_pacman_size_str(v)
                elif k == "Packager":
                    info["packager"] = v
                elif k == "Repository":
                    info["repository"] = v
                elif k == "Depends On":
                    info["depends"] = [d for d in v.split() if d and d != "None"]

        self._pkg_info_cache[packagename] = info
        return info

    def controlPackageCache(self, packagename):
        info = self._query_pacman_si(packagename)
        return bool(info.get("version"))

    def isinstalled(self, packagename):
        res = subprocess.run(["pacman", "-Q", packagename],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0

    def missingdeps(self, packagename):
        return False

    def get_depends(self, packagename):
        info = self._query_pacman_si(packagename)
        return info.get("depends", [])

    def get_rdepends(self, packagename, only_upgradable=False):
        # Optional reverse dependency lookup
        rdepends = []
        res = subprocess.run(["pacman", "-Sii", packagename], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             env={**os.environ, "LC_ALL": "C"})
        if res.returncode == 0:
            for line in res.stdout.decode("utf-8", errors="ignore").splitlines():
                if line.startswith("Required By"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        rdepends = [p for p in parts[1].split() if p and p != "None"]
        return rdepends

    def description(self, packagename, israw=False):
        info = self._query_pacman_si(packagename)
        desc = info.get("description", "")
        if not desc:
            return "Description is not found"
        return desc.replace("\n", "") if israw else desc

    def adv_description(self, packagename):
        return self.description(packagename, False)

    def summary(self, packagename):
        info = self._query_pacman_si(packagename)
        summary = info.get("description", "")
        return summary if summary else "Summary is not found"

    def candidate_version(self, packagename):
        if packagename in self._upgradable_cache:
            return self._upgradable_cache[packagename].get("new_version", "")
        info = self._query_pacman_si(packagename)
        return info.get("version", "")

    def installed_version(self, packagename):
        res = subprocess.run(["pacman", "-Q", packagename], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             env={**os.environ, "LC_ALL": "C"})
        if res.returncode == 0:
            parts = res.stdout.decode("utf-8", errors="ignore").strip().split()
            if len(parts) >= 2:
                return parts[1]
        return ""

    def size(self, packagename):
        info = self._query_pacman_si(packagename)
        size_bytes = info.get("download_size", 0) or info.get("installed_size", 0)
        return self.beauty_size(size_bytes)

    def get_records(self, packagename):
        info = self._query_pacman_si(packagename)
        packager = info.get("packager", "")
        maintainer_name = packager.split(" <")[0] if " <" in packager else packager
        maintainer_mail = packager.split(" <")[1].replace(">", "") if " <" in packager else ""
        homepage = info.get("url", "")
        arch = info.get("architecture", "")
        return maintainer_name, maintainer_mail, homepage, arch

    def get_uri(self, packagename):
        info = self._query_pacman_si(packagename)
        return bool(info.get("url")), info.get("url", "")

    def get_section(self, packagename):
        info = self._query_pacman_si(packagename)
        return info.get("repository", "extra").lower()

    def _fetch_upgrades_raw(self):
        """Runs checkupdates or pacman -Qu to gather upgradable packages."""
        updates = {}
        # Try checkupdates first
        if shutil.which("checkupdates"):
            res = subprocess.run(["checkupdates", "--nocolor"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 env={**os.environ, "LC_ALL": "C"})
            if res.returncode in (0, 2):  # 0: updates found, 2: no updates
                for line in res.stdout.decode("utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if " -> " in line:
                        parts = line.split()
                        if len(parts) >= 4 and parts[2] == "->":
                            name = parts[0]
                            old_ver = parts[1]
                            new_ver = parts[3]
                            updates[name] = {"name": name, "old_version": old_ver, "new_version": new_ver}
                return updates

        # Fallback to pacman -Qu
        res = subprocess.run(["pacman", "-Qu"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env={**os.environ, "LC_ALL": "C"})
        if res.returncode == 0:
            for line in res.stdout.decode("utf-8", errors="ignore").splitlines():
                line = line.strip()
                if " -> " in line:
                    parts = line.split()
                    if len(parts) >= 4 and parts[2] == "->":
                        name = parts[0]
                        old_ver = parts[1]
                        new_ver = parts[3]
                        updates[name] = {"name": name, "old_version": old_ver, "new_version": new_ver}
                elif line:
                    parts = line.split()
                    if parts:
                        name = parts[0]
                        updates[name] = {"name": name, "old_version": "", "new_version": parts[1] if len(parts) > 1 else ""}

        return updates

    def upgradable(self):
        """Returns list of upgradable package names."""
        self._upgradable_cache = self._fetch_upgrades_raw()
        return sorted(list(self._upgradable_cache.keys()))

    def upgradable_full(self):
        """Returns list of dicts with name and summary."""
        names = self.upgradable()
        result = []
        for name in names:
            result.append({"name": name, "summary": self.summary(name)})
        return sorted(result, key=lambda x: x["name"])

    def autoremovable(self):
        """Returns orphaned packages (installed as dependencies but no longer needed)."""
        orphans = []
        res = subprocess.run(["pacman", "-Qdtq"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             env={**os.environ, "LC_ALL": "C"})
        if res.returncode == 0:
            for line in res.stdout.decode("utf-8", errors="ignore").splitlines():
                pkg = line.strip()
                if pkg:
                    orphans.append(pkg)
        return sorted(orphans)

    def residual(self):
        """Arch Linux doesn't maintain dpkg residual config files."""
        return []

    def required_changes_upgrade(self, sleep=True, keep_list=None):
        if sleep:
            time.sleep(0.2)

        upgrades = self._fetch_upgrades_raw()
        self._upgradable_cache = upgrades

        to_upgrade = []
        to_install = []
        to_delete = []
        to_keep = []
        user_keep_list_depends = []
        keep_set = set(keep_list or [])

        download_size = 0
        install_size = 0

        for pkg, data in upgrades.items():
            if pkg in keep_set:
                to_keep.append(pkg)
            else:
                to_upgrade.append(pkg)
                info = self._query_pacman_si(pkg)
                d_sz = info.get("download_size", 0)
                i_sz = info.get("installed_size", 0)
                download_size += d_sz
                install_size += i_sz

        changes_available = bool(to_upgrade or to_install or to_delete)
        cache_error = False

        rcu = {
            "download_size": download_size,
            "freed_size": 0,
            "install_size": install_size,
            "to_upgrade": sorted(to_upgrade),
            "to_install": sorted(to_install),
            "to_delete": sorted(to_delete),
            "to_keep": sorted(to_keep),
            "changes_available": changes_available,
            "cache_error": cache_error,
            "user_keep_list_depends": user_keep_list_depends,
        }
        return rcu

    def required_changes_autoremove(self, packages, sleep=True):
        if sleep:
            time.sleep(0.2)

        to_delete = []
        install_size = 0
        freed_size = 0

        for pkg in packages:
            if self.isinstalled(pkg):
                to_delete.append(pkg)
                info = self._query_pacman_si(pkg)
                freed_size += info.get("installed_size", 0)

        ret = {
            "download_size": 0,
            "freed_size": freed_size,
            "install_size": install_size,
            "to_install": [],
            "to_delete": to_delete,
            "broken": [],
            "package_broken": False,
        }
        return ret

    def get_appname_from_desktopfile(self, desktopname):
        """Finds which package owns a desktop file using pacman -Qo."""
        for target in [desktopname, os.path.basename(desktopname)]:
            res = subprocess.run(["pacman", "-Qo", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 env={**os.environ, "LC_ALL": "C"})
            if res.returncode == 0:
                output = res.stdout.decode("utf-8", errors="ignore").strip()
                if "is owned by " in output:
                    pkg = output.split("is owned by ")[1].split()[0]
                    return True, pkg
        return False, ""

    def myapps_remove_details(self, desktopname):
        success, pkg = self.get_appname_from_desktopfile(desktopname)
        if success and pkg:
            info = self._query_pacman_si(pkg)
            changes = {
                "download_size": 0,
                "freed_size": info.get("installed_size", 0),
                "install_size": 0,
                "to_install": [],
                "to_delete": [pkg],
                "broken": [],
                "package_broken": False,
            }
            return True, changes, pkg
        return False, None, ""

    def beauty_size(self, size):
        if not isinstance(size, (int, float)):
            return "size not found"
        if GLib:
            return GLib.format_size(int(size))
        # Simple fallback
        for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
            if size < 1024.0:
                return "{:.1f} {}".format(size, unit)
            size /= 1024.0
        return "{:.1f} PiB".format(size)

    def get_installed_apps(self):
        apps = []
        if not Gio:
            return apps
        for app in Gio.DesktopAppInfo.get_all():
            id = app.get_id()
            name = app.get_name()
            executable = app.get_executable()
            nodisplay = app.get_nodisplay()
            icon = app.get_string("Icon")
            description = app.get_description() or app.get_generic_name() or app.get_name()
            filename = app.get_filename()
            keywords = " ".join(app.get_keywords() or [])

            if executable and not nodisplay:
                apps.append({
                    "id": id, "name": name, "icon": icon, "description": description,
                    "filename": filename, "keywords": keywords, "executable": executable
                })

        apps = sorted(dict((v["name"], v) for v in apps).values(), key=lambda x: locale.strxfrm(x["name"]))
        return apps

    def parse_desktopfile(self, desktopfilename):
        if not Gio:
            return False, None
        try:
            app = Gio.DesktopAppInfo.new(desktopfilename)
            if app:
                return True, {
                    "id": app.get_id(),
                    "name": app.get_name(),
                    "icon": app.get_string("Icon"),
                    "description": app.get_description() or app.get_generic_name() or app.get_name(),
                    "filename": app.get_filename(),
                    "keywords": " ".join(app.get_keywords() or []),
                    "executable": app.get_executable()
                }
        except Exception as e:
            print("parse_desktopfile error: {}".format(e))
        return False, None

    def origins(self, packagename):
        info = self._query_pacman_si(packagename)
        return info.get("repository", "extra")

    def get_sources(self):
        """Parses /etc/pacman.d/mirrorlist and returns mirrors."""
        repos = {}
        mirrorlist = "/etc/pacman.d/mirrorlist"
        if os.path.exists(mirrorlist):
            try:
                with open(mirrorlist, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("Server"):
                            parts = line.split("=", 1)
                            if len(parts) == 2:
                                url = parts[1].strip()
                                repos.setdefault(url, []).append({
                                    "file": mirrorlist,
                                    "comps": ["core", "extra", "multilib"],
                                    "disabled": False,
                                    "dist": "arch",
                                    "type": "binary",
                                    "uri": url,
                                    "line": line,
                                    "architectures": ["x86_64"]
                                })
            except Exception as e:
                print("Error reading mirrorlist: {}".format(e))
        return repos

    def versionCompare(self, version1, version2):
        if not version2 or version2 == "None":
            return False
        # Use pacman's native vercmp binary
        if shutil.which("vercmp"):
            res = subprocess.run(["vercmp", str(version1), str(version2)],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 env={**os.environ, "LC_ALL": "C"})
            try:
                val = int(res.stdout.decode("utf-8").strip())
                return val
            except ValueError:
                pass

        # Fallback comparison
        if version1 == version2:
            return 0
        return 1 if version1 > version2 else -1

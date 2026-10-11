#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System update actions executed via pkexec for Pars Update.
Supports Debian/APT and Arch Linux/Pacman.
"""

import json
import locale
import os
import re
import subprocess
import sys
from pathlib import Path
from shutil import rmtree

from PackageManagerBackend import get_package_manager

try:
    import apt
    import apt_pkg
    HAVE_APT = True
except ImportError:
    HAVE_APT = False
    apt = None
    apt_pkg = None

locale.bindtextdomain('pars-update', '/usr/share/locale')
locale.textdomain('pars-update')


def main():
    keep_list = ["firmware-b43-installer", "firmware-b43legacy-installer", "ttf-mscorefonts-installer"]
    backend = get_package_manager()

    def parse_packages(packages):
        if not packages or not packages.strip():
            return []

        packagelist = packages.split()
        valid_packages = []

        package_re = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9+._-]+(?::[a-zA-Z0-9]+)?$')

        for item in packagelist:
            item = item.strip()
            if not item:
                continue

            if package_re.fullmatch(item):
                valid_packages.append(item)
            else:
                raise ValueError(f"Invalid package name detected: '{item}'")

        return valid_packages

    # ---------------- Pacman (Arch Linux) Implementations ----------------
    def pacman_control_lock():
        lock_path = "/var/lib/pacman/db.lck"
        if os.path.exists(lock_path):
            msg = "pacman database locked (/var/lib/pacman/db.lck)"
            print("pars-update: {}".format(msg), file=sys.stderr)
            return False, msg
        return True, ""

    def pacman_subupdate():
        subprocess.call(["pacman", "-Sy"],
                        env={**os.environ, 'LC_ALL': 'C'})

    def pacman_subupgrade(yq_state, dpkg_conf_state, keeps=None):
        lock, msg = pacman_control_lock()
        if not lock:
            print("pacman lock error", file=sys.stderr)
            sys.exit(11)

        cmd = ["pacman", "-Syu"]
        if yq_state == "yes":
            cmd.append("--noconfirm")

        try:
            valid_keeps = parse_packages(keeps)
        except ValueError as e:
            print(f"Security Alert: {e}", file=sys.stderr)
            sys.exit(1)

        if valid_keeps:
            cmd.extend(["--ignore", ",".join(valid_keeps)])

        result = subprocess.run(cmd, env={**os.environ, "LC_ALL": "C"})
        sys.exit(result.returncode)

    def pacman_removeauto():
        res = subprocess.run(["pacman", "-Qdtq"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             env={**os.environ, "LC_ALL": "C"})
        orphans = [p.strip() for p in res.stdout.decode("utf-8", errors="ignore").splitlines() if p.strip()]
        if orphans:
            cmd = ["pacman", "-Rns", "--noconfirm"] + orphans
            result = subprocess.run(cmd, env={**os.environ, "LC_ALL": "C"})
            sys.exit(result.returncode)
        else:
            print("No orphaned packages to remove.", file=sys.stdout)
            sys.exit(0)

    def pacman_aptclear(clean, autoremove, aptlists):
        if clean == "1":
            subprocess.call(["pacman", "-Sc", "--noconfirm"],
                            env={**os.environ, "LC_ALL": "C"})
            print("pacman package cache cleared", file=sys.stdout)
        if autoremove == "1":
            res = subprocess.run(["pacman", "-Qdtq"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                 env={**os.environ, "LC_ALL": "C"})
            orphans = [p.strip() for p in res.stdout.decode("utf-8", errors="ignore").splitlines() if p.strip()]
            if orphans:
                subprocess.call(["pacman", "-Rns", "--noconfirm"] + orphans,
                                env={**os.environ, "LC_ALL": "C"})
        if aptlists == "1":
            subprocess.call(["pacman", "-Syy", "--noconfirm"],
                            env={**os.environ, "LC_ALL": "C"})

    def pacman_dpkgconfigure():
        lock_path = "/var/lib/pacman/db.lck"
        if os.path.exists(lock_path):
            print("Checking pacman lock: lock exists.", file=sys.stderr)

    # ---------------- APT (Debian) Implementations ----------------
    def control_lock():
        if not HAVE_APT:
            return pacman_control_lock()
        msg = ""
        apt_pkg.init_system()
        try:
            apt_pkg.pkgsystem_lock()
        except SystemError as e:
            msg = "{}".format(e)
            print("pars-update: {}".format(msg), file=sys.stderr)
            return False, msg
        apt_pkg.pkgsystem_unlock()
        return True, msg

    def subupdate():
        if backend == "pacman" or not HAVE_APT:
            return pacman_subupdate()
        subprocess.call(["apt", "update"],
                        env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'})

    def subupgrade(yq_state, dpkg_conf_state, keeps=None):
        if backend == "pacman" or not HAVE_APT:
            return pacman_subupgrade(yq_state, dpkg_conf_state, keeps)

        lock, msg = control_lock()
        if not lock:
            if "E:" in msg and "/var/lib/dpkg/lock-frontend" in msg:
                print("dpkg lock error", file=sys.stderr)
                sys.exit(11)
            elif "E:" in msg and "dpkg --configure -a" in msg:
                print("dpkg interrupt error", file=sys.stderr)
                sys.exit(12)

        if yq_state == "yes":
            yq_args = ["-y", "-q"]
        elif yq_state == "ask":
            yq_args = []
        else:
            print("Invalid enum for yq_state. Aborting.", file=sys.stderr)
            sys.exit(1)

        if dpkg_conf_state == "new":
            dpkg_args = ["-o", "Dpkg::Options::=--force-confnew"]
        elif dpkg_conf_state == "old":
            dpkg_args = ["-o", "Dpkg::Options::=--force-confold"]
        elif dpkg_conf_state == "ask":
            dpkg_args = []
        else:
            print("Invalid enum for dpkg_conf_state. Aborting.", file=sys.stderr)
            sys.exit(1)

        try:
            valid_keeps = parse_packages(keeps)
        except ValueError as e:
            print(f"Security Alert: {e}", file=sys.stderr)
            sys.exit(1)

        if valid_keeps:
            for kp in valid_keeps:
                subprocess.call(["apt-mark", "hold", kp])

        result = subprocess.run(["apt", "full-upgrade"] + yq_args + dpkg_args,
                                env={**os.environ, "DEBIAN_FRONTEND": "noninteractive"})

        if valid_keeps:
            for kp in valid_keeps:
                subprocess.call(["apt-mark", "unhold", kp])

        sys.exit(result.returncode)

    def dpkgconfigure():
        if backend == "pacman" or not HAVE_APT:
            return pacman_dpkgconfigure()
        subprocess.call(["dpkg", "--configure", "-a"],
                        env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'})

    def aptclean():
        if backend == "pacman" or not HAVE_APT:
            return pacman_aptclear("1", "0", "0")
        subprocess.call(["apt", "clean"],
                        env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'})

    def removeresidual(packages):
        if backend == "pacman" or not HAVE_APT:
            print("No residual packages on Arch Linux.", file=sys.stdout)
            sys.exit(0)

        try:
            valid_packages = parse_packages(packages)
        except ValueError as e:
            print(f"SECURITY ALERT: {e}", file=sys.stderr)
            sys.exit(1)

        if not valid_packages:
            print("No packages to remove.", file=sys.stdout)
            sys.exit(0)

        try:
            cache = apt.Cache()
            cache.open()
        except Exception as e:
            print(f"Could not open apt cache. Aborting. Error: {e}", file=sys.stderr)
            sys.exit(1)

        verified_residuals = []
        for pkg in valid_packages:
            if pkg in cache:
                if cache[pkg].has_config_files and not cache[pkg].is_installed:
                    verified_residuals.append(pkg)
                else:
                    print(f"Package '{pkg}' is not in residual state.", file=sys.stderr)
            else:
                print(f"Package '{pkg}' not found in apt cache.", file=sys.stderr)

        if verified_residuals:
            subprocess.call(["apt", "remove", "--purge", "-yq"] + verified_residuals,
                            env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'})

    def removeauto():
        if backend == "pacman" or not HAVE_APT:
            return pacman_removeauto()
        subprocess.call(["apt", "autoremove", "-yq"],
                        env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'})

    def controldistupgrade(sourceslist):
        if backend == "pacman" or not HAVE_APT:
            print("Distribution upgrade sources not applicable for Arch rolling release.", file=sys.stderr)
            sys.exit(0)

        if not is_safe_sources(sourceslist):
            print("Malicious apt source detected. Execution aborted.", file=sys.stderr)
            sys.exit(1)

        sfile = open("/tmp/tmp-sources.list", "w")
        sfile.write(sourceslist)
        sfile.flush()
        sfile.close()

        rc_file = os.path.dirname(os.path.abspath(__file__)) + "/../required_changes_for_upgrade.json"

        if os.path.isfile(rc_file):
            os.remove(rc_file)

        to_upgrade = []
        to_install = []
        to_delete = []
        to_keep = []
        changes_available = None
        cache_error = True

        rcu = {"download_size": None, "freed_size": None, "install_size": None, "to_upgrade": None, "to_install": None,
               "to_delete": None, "to_keep": None, "changes_available": changes_available, "cache_error": cache_error,
               "cache_error_msg": None}

        old_sources_list = apt_pkg.config.find("Dir::Etc::sourcelist")
        old_sources_list_d = apt_pkg.config.find("Dir::Etc::sourceparts")
        old_cleanup = apt_pkg.config.find("APT::List-Cleanup")
        apt_pkg.init_config()
        apt_pkg.config.set("Dir::Etc::sourcelist", os.path.abspath("/tmp/tmp-sources.list"))
        apt_pkg.config.set("Dir::Etc::sourceparts", "xxx")
        apt_pkg.config.set("APT::List-Cleanup", "0")
        apt_pkg.init_system()
        cache = apt.Cache()
        cache.update()
        cache.open()

        try:
            cache.upgrade(True)
            cache_error = False
        except Exception as error:
            print("cache.upgrade Error: {}".format(error))
            update_cache_error_msg = "{}".format(error)
            rcu["cache_error_msg"] = update_cache_error_msg

        for kp in keep_list:
            try:
                cache[kp].mark_keep()
            except Exception as e:
                print("{} not found: {}".format(kp, e))

        changes = cache.get_changes()
        if changes:
            changes_available = True
            for package in changes:
                if package.is_installed:
                    if package.marked_upgrade:
                        to_upgrade.append(package.name)
                    elif package.marked_delete:
                        to_delete.append(package.name)
                elif package.marked_install:
                    to_install.append(package.name)
        else:
            changes_available = False

        download_size = cache.required_download
        space = cache.required_space
        if space < 0:
            freed_size = space * -1
            install_size = 0
        else:
            freed_size = 0
            install_size = space

        if cache.keep_count > 0:
            upgradable_cache_packages = [pkg.name for pkg in cache if pkg.is_upgradable]
            upgradable_changes_packages = [pkg.name for pkg in changes if pkg.is_upgradable]
            to_keep = list(set(upgradable_cache_packages).difference(set(upgradable_changes_packages)))

        rcu["download_size"] = download_size
        rcu["freed_size"] = freed_size
        rcu["install_size"] = install_size
        rcu["changes_available"] = changes_available
        rcu["cache_error"] = cache_error

        def summary(packagename):
            package = cache.get(packagename)
            if package is None:
                return ""
            try:
                return package.candidate.summary
            except AttributeError:
                sum = package.versions.get(0)
            return sum.summary if hasattr(sum, "summary") else "Summary is not found"

        def candidate_version(packagename):
            package = cache[packagename]
            if package is None:
                return ""
            try:
                version = package.candidate.version
            except:
                try:
                    version = package.versions[0].version
                except:
                    version = ""
            return version

        def installed_version(packagename):
            package = cache[packagename]
            if package is None:
                return ""
            try:
                version = package.installed.version
            except:
                version = ""
            return version

        to_install_list = []
        for package in to_install:
            to_install_list.append({"name": package, "oldversion": installed_version(package),
                                    "newversion": candidate_version(package), "summary": summary(package)})

        to_upgrade_list = []
        for package in to_upgrade:
            to_upgrade_list.append({"name": package, "oldversion": installed_version(package),
                                    "newversion": candidate_version(package), "summary": summary(package)})

        to_delete_list = []
        for package in to_delete:
            to_delete_list.append({"name": package, "oldversion": installed_version(package),
                                    "newversion": candidate_version(package), "summary": summary(package)})

        to_keep_list = []
        for package in to_keep:
            to_keep_list.append({"name": package, "oldversion": installed_version(package),
                                 "newversion": candidate_version(package), "summary": summary(package)})

        rcu["to_upgrade"] = to_upgrade_list
        rcu["to_install"] = to_install_list
        rcu["to_delete"] = to_delete_list
        rcu["to_keep"] = to_keep_list

        with open(rc_file, "w") as changes_file:
            json.dump(rcu, changes_file, indent=2)

        apt_pkg.config.set("Dir::Etc::sourcelist", old_sources_list)
        apt_pkg.config.set("Dir::Etc::sourceparts", old_sources_list_d)
        apt_pkg.config.set("APT::List-Cleanup", old_cleanup)

    def downupgrade(sourceslist):
        if backend == "pacman" or not HAVE_APT:
            return
        if not is_safe_sources(sourceslist):
            print("Malicious apt source detected. Execution aborted.", file=sys.stderr)
            sys.exit(1)

        aptclean()
        sfile = open("/tmp/tmp-sources.list", "w")
        sfile.write(sourceslist)
        sfile.flush()
        sfile.close()

        apt_pkg.init_config()
        apt_pkg.config.set("Dir::Etc::sourcelist", os.path.abspath("/tmp/tmp-sources.list"))
        apt_pkg.config.set("Dir::Etc::sourceparts", "xxx")
        apt_pkg.config.set("APT::List-Cleanup", "0")
        apt_pkg.init_system()
        cache = apt.Cache()
        cache.update()
        cache.open()

        try:
            cache.upgrade(True)
        except Exception as error:
            print("cache.upgrade Error: {}".format(error))

        for kp in keep_list:
            try:
                cache[kp].mark_keep()
            except Exception as e:
                print("{} not found: {}".format(kp, e))

        cache.fetch_archives()

    def distupgradeoffline(sourceslist, askconf):
        if backend == "pacman" or not HAVE_APT:
            return

        if not is_safe_sources(sourceslist):
            print("Malicious apt source detected. Execution aborted.", file=sys.stderr)
            sys.exit(1)

        if askconf == "new":
            askconf_arg = "--force-confnew"
        elif askconf == "old":
            askconf_arg = "--force-confold"
        else:
            print("Invalid enum for askconf. Aborting.", file=sys.stderr)
            sys.exit(1)

        app_safeupgrade_path = os.path.dirname(os.path.abspath(__file__)) + "/../data/pars-safeupgrade-template.sh"
        safeupgrade_path = os.path.dirname(os.path.abspath(__file__)) + "/../data/pars-safeupgrade.sh"
        app_service_path = os.path.dirname(os.path.abspath(__file__)) + "/../data/pars-safeupgrade.service"
        service_path = "/usr/lib/systemd/system/pars-safeupgrade.service"
        service_symlink_path = "/usr/lib/systemd/system/system-update.target.wants/pars-safeupgrade.service"
        service_symlink_dir = "/usr/lib/systemd/system/system-update.target.wants"

        if os.path.isfile(app_safeupgrade_path) and os.path.isfile(app_service_path):
            with open(app_safeupgrade_path, "r") as app_safeupgrade_file:
                contents = app_safeupgrade_file.read()
                new_contents = contents.replace("@@askconf@@", askconf_arg)

            with open(safeupgrade_path, "w") as usp:
                usp.write(new_contents)
            os.chmod(safeupgrade_path, 0o0755)

            with open(app_service_path, "r") as app_service_file:
                scontents = app_service_file.read()
                new_scontents = scontents.replace("@@execpath@@", os.path.abspath(safeupgrade_path))

            with open(service_path, "w") as user_service_file:
                user_service_file.write(new_scontents)

            if not os.path.exists(service_symlink_dir):
                os.makedirs(service_symlink_dir, exist_ok=True)
            service_symlink_file = Path(service_symlink_path)
            if service_symlink_file.exists():
                service_symlink_file.unlink(missing_ok=True)
            service_symlink_file.symlink_to(service_path)

            sdir = "/etc/apt/sources.list.d"
            if os.path.isdir(sdir):
                for slist in os.listdir(sdir):
                    if slist.endswith(".list"):
                        try:
                            with open(os.path.join(sdir, slist), "r") as sread:
                                commented = "".join(["#{}".format(line) for line in sread.readlines()])
                            with open(os.path.join(sdir, slist), "w") as swrite:
                                swrite.write(commented)
                        except Exception as e:
                            print("{}".format(e))

            with open("/etc/apt/sources.list", "w") as sfile:
                sfile.write(sourceslist)

            rmtree("/var/lib/apt/lists/", ignore_errors=True)
            subupdate()

            current_theme = ""
            try:
                with open("/etc/plymouth/plymouthd.conf", "r") as f:
                    for line in f:
                        if line.strip().startswith("Theme="):
                            current_theme = line.strip().split("=", 1)[1]
                            break
            except Exception:
                current_theme = ""
            if current_theme != "bgrt":
                subprocess.run(["plymouth-set-default-theme", "bgrt"])
                subprocess.run(["update-initramfs", "-u"])

            sup_path = "/system-update"
            if os.path.exists(sup_path):
                os.remove(sup_path)
            with open(sup_path, "w"):
                pass

            subprocess.run(["/usr/bin/sync"])

            if os.path.exists(safeupgrade_path) and os.path.exists(service_path) and os.path.exists(sup_path):
                os.system('dbus-send --system --print-reply --dest=org.freedesktop.login1 /org/freedesktop/login1 '
                          '"org.freedesktop.login1.Manager.Reboot" boolean:true')
            else:
                if os.path.exists(sup_path):
                    os.remove(sup_path)
        else:
            print("{} file not exists.".format(app_safeupgrade_path))

    def aptclear(clean, autoremove, aptlists):
        if backend == "pacman" or not HAVE_APT:
            return pacman_aptclear(clean, autoremove, aptlists)
        if clean == "1":
            aptclean()
            print("apt cache files cleared", file=sys.stdout)
        if autoremove == "1":
            removeauto()
        if aptlists == "1":
            rmtree("/var/lib/apt/lists/", ignore_errors=True)
            subupdate()

    def is_safe_sources(sources_text):
        if not sources_text or not str(sources_text).strip():
            return False

        blacklisted_terms = [
            "trusted=yes", "trusted=true",
            "allow-insecure",
            "signed-by=",
            "file://", "copy://", "cdrom://"
        ]

        for line in str(sources_text).splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if not re.match(r"^deb(-src)?\s+", line):
                return False

            compact_line = line.lower().replace(" ", "")
            for term in blacklisted_terms:
                if term.replace(" ", "") in compact_line:
                    return False

        return True

    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "upgrade":
            subupdate()
            subupgrade(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
        elif action == "removeresidual":
            removeresidual(sys.argv[2])
        elif action == "removeauto":
            removeauto()
        elif action == "controldistupgrade":
            aptclean()
            controldistupgrade(sys.argv[2])
        elif action == "downupgrade":
            downupgrade(sys.argv[2])
        elif action == "distupgradeoffline":
            distupgradeoffline(sys.argv[2], sys.argv[3])
        elif action == "dpkgconfigure":
            dpkgconfigure()
        elif action == "aptclear":
            aptclear(sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            print("unknown argument error")
    else:
        print("no argument passed")


if __name__ == "__main__":
    main()

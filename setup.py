#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

from setuptools import setup, find_packages


def create_mo_files():
    podir = "po"
    mo = []
    for po in os.listdir(podir):
        if po.endswith(".po"):
            os.makedirs("{}/{}/LC_MESSAGES".format(podir, po.split(".po")[0]), exist_ok=True)
            mo_file = "{}/{}/LC_MESSAGES/{}".format(podir, po.split(".po")[0], "pars-update.mo")
            msgfmt_cmd = 'msgfmt {} -o {}'.format(podir + "/" + po, mo_file)
            subprocess.call(msgfmt_cmd, shell=True)
            mo.append(("/usr/share/locale/" + po.split(".po")[0] + "/LC_MESSAGES",
                       ["po/" + po.split(".po")[0] + "/LC_MESSAGES/pars-update.mo"]))
    return mo


changelog = "debian/changelog"
if os.path.exists(changelog):
    head = open(changelog).readline()
    try:
        version = head.split("(")[1].split(")")[0]
    except:
        print("debian/changelog format is wrong for get version")
        version = "0.0.0"
    f = open("src/__version__", "w")
    f.write(version)
    f.close()

data_files = [
                 ("/usr/bin", ["pars-update"]),
                 ("/usr/share/applications",
                  ["data/org.pars.update.desktop"]),
                 ("/usr/share/pars/pars-update/ui",
                  ["ui/MainWindow.glade"]),
                 ("/usr/share/pars/pars-update/src",
                  ["src/AptSourceActions.py",
                   "src/AutoAptUpdate.py",
                   "src/Group.py",
                   "src/Main.py",
                   "src/MainWindow.py",
                   "src/Package.py",
                   "src/PackageManagerBackend.py",
                   "src/RepoDistControl.py",
                   "src/SysActions.py",
                   "src/SystemSettings.py",
                   "src/SystemSettingsWrite.py",
                   "src/UserSettings.py",
                   "src/Utils.py",
                   "src/__version__"]),
                 ("/usr/share/pars/pars-update/data",
                  ["data/org.pars.update-autostart.desktop",
                   "data/pars-update.svg",
                   "data/pars-update-available-symbolic.svg",
                   "data/pars-update-error-symbolic.svg",
                   "data/pars-update-inprogress-symbolic.svg",
                   "data/pars-update-symbolic.svg",
                   "data/pars-update-uptodate.svg",
                   "data/pars-update-cantconnect.svg",
                   "data/pars-safeupgrade-template.sh",
                   "data/pars-safeupgrade.service",
                   "data/style.css",
                   "data/sources.json"]),
                 ("/usr/share/polkit-1/actions",
                  ["data/org.pars.pkexec.pars-update.policy"]),
                 ("/etc/skel/.config/autostart",
                  ["data/org.pars.update-autostart.desktop"]),
                 ("/usr/share/icons/hicolor/scalable/apps/",
                  ["data/pars-update.svg",
                   "data/pars-update-available-symbolic.svg",
                   "data/pars-update-error-symbolic.svg",
                   "data/pars-update-inprogress-symbolic.svg",
                   "data/pars-update-symbolic.svg",
                   "data/pars-update-uptodate.svg",
                   "data/pars-update-cantconnect.svg"]),
                 ("/usr/share/polkit-1/rules.d/",
                  ["data/pars-update-group.rules"])
             ] + create_mo_files()

setup(
    name="pars-update",
    version=version,
    packages=find_packages(),
    scripts=["pars-update"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Fatih Altun",
    author_email="fatih.altun@pardus.org.tr",
    description="Pars Update application",
    license="GPLv3",
    keywords="pars-update, update, upgrade, apt",
    url="https://github.com/pars/pars-update",
)

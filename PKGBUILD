# Maintainer: Pars Linux Team <info@parslinux.org>
pkgname=pars-update
pkgver=1.4.3
pkgrel=1
pkgdesc="Modern system update manager for Pars Linux, Arch Linux and Debian derivatives"
arch=('any')
url="https://github.com/parslinux/pars-update"
license=('GPL-3.0-or-later')
depends=(
    'python'
    'python-gobject'
    'gtk3'
    'libnotify'
    'libsoup'
    'vte3'
    'libappindicator-gtk3'
    'polkit'
    'pacman-contrib'
)
makedepends=(
    'python-setuptools'
    'gettext'
)
optdepends=(
    'python-distro: Enhanced distribution detection'
)
source=("$pkgname-$pkgver.tar.gz::$url/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
    cd "$srcdir/$pkgname-$pkgver" 2>/dev/null || cd "$srcdir" 2>/dev/null || true
    python setup.py build
}

package() {
    cd "$srcdir/$pkgname-$pkgver" 2>/dev/null || cd "$srcdir" 2>/dev/null || true
    python setup.py install --prefix=/usr --root="$pkgdir" --optimize=1
}

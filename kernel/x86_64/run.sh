#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD="${1:-$HERE/build}"
ISO_ROOT="$BUILD/isofiles"

command -v grub-mkrescue >/dev/null 2>&1 || {
    echo "grub-mkrescue is required" >&2
    exit 1
}
command -v qemu-system-x86_64 >/dev/null 2>&1 || {
    echo "qemu-system-x86_64 is required" >&2
    exit 1
}

"$HERE/build.sh" "$BUILD"

rm -rf "$ISO_ROOT"
mkdir -p "$ISO_ROOT/boot/grub"
cp "$BUILD/flow-kernel.elf" "$ISO_ROOT/boot/flow-kernel.elf"
cp "$HERE/grub.cfg" "$ISO_ROOT/boot/grub/grub.cfg"

grub-mkrescue -o "$BUILD/flow-kernel.iso" "$ISO_ROOT" >/dev/null 2>&1

exec qemu-system-x86_64 \
    -cdrom "$BUILD/flow-kernel.iso" \
    -serial stdio \
    -display none \
    -no-reboot \
    -no-shutdown

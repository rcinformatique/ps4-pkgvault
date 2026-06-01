#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import sys
from pathlib import Path


def read_pkg_header(pkg_file):
    with open(pkg_file, "rb") as f:

        # Magic
        magic = struct.unpack(">I", f.read(4))[0]

        # Nombre d'entrées
        f.seek(0x10)
        entry_count = struct.unpack(">H", f.read(2))[0]

        # Offset table
        f.seek(0x18)
        table_offset = struct.unpack(">I", f.read(4))[0]

        # Content ID
        f.seek(0x40)
        content_id = (
            f.read(36)
            .split(b"\x00")[0]
            .decode("ascii", errors="ignore")
        )

    return {
        "magic": f"0x{magic:08X}",
        "entry_count": entry_count,
        "table_offset": table_offset,
        "content_id": content_id,
    }


def list_entries(pkg_file):
    entries = []

    with open(pkg_file, "rb") as f:

        f.seek(0x10)
        entry_count = struct.unpack(">H", f.read(2))[0]

        f.seek(0x18)
        table_offset = struct.unpack(">I", f.read(4))[0]

        for i in range(min(entry_count, 100)):

            pos = table_offset + (i * 32)

            f.seek(pos)

            entry_id = struct.unpack(">I", f.read(4))[0]

            f.read(12)

            offset = struct.unpack(">I", f.read(4))[0]
            size = struct.unpack(">I", f.read(4))[0]

            entries.append({
                "id": f"0x{entry_id:04X}",
                "offset": offset,
                "size": size
            })

    return entries


def main():

    if len(sys.argv) != 2:
        print("Usage : python read_pkg.py fichier.pkg")
        return

    pkg = Path(sys.argv[1])

    if not pkg.exists():
        print("Fichier introuvable")
        return

    print("=" * 60)
    print("LECTURE PKG PS4")
    print("=" * 60)

    print(f"Fichier : {pkg.name}")
    print(f"Taille  : {pkg.stat().st_size:,} octets")

    header = read_pkg_header(pkg)

    print("\nHEADER")
    print("-" * 60)
    print("Magic      :", header["magic"])
    print("Entrées    :", header["entry_count"])
    print("Table      :", header["table_offset"])
    print("Content ID :", header["content_id"])

    print("\nENTRÉES")
    print("-" * 60)

    for entry in list_entries(pkg):
        print(
            f"{entry['id']:>10} | "
            f"Offset: {entry['offset']:>10} | "
            f"Size: {entry['size']:>10}"
        )


if __name__ == "__main__":
    main()
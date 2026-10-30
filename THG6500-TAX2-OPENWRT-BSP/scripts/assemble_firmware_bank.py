#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Replace kernel/rootfs payloads while preserving vendor bank metadata."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


KERNEL_SIZE = 8 * 1024 * 1024
BANK_SIZE = 40 * 1024 * 1024
METADATA_MARKER = b"fullimage=0crc32="


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", type=Path, help="original 40 MiB inactive bank")
    parser.add_argument("kernel", type=Path, help="unchanged inactive-bank kernel")
    parser.add_argument("rootfs_ubi", type=Path, help="rebuilt rootfs UBI image")
    parser.add_argument("output", type=Path, help="40 MiB bank image")
    args = parser.parse_args()

    template = args.template.read_bytes()
    kernel = args.kernel.read_bytes()
    rootfs = args.rootfs_ubi.read_bytes()
    if len(template) != BANK_SIZE:
        raise SystemExit(f"Template bank must be exactly {BANK_SIZE} bytes")
    if len(kernel) != KERNEL_SIZE:
        raise SystemExit(f"Kernel must be exactly {KERNEL_SIZE} bytes")

    metadata_offset = template.find(METADATA_MARKER, KERNEL_SIZE)
    if metadata_offset < 0:
        raise SystemExit("Vendor metadata marker not found in template bank")
    rootfs_end = KERNEL_SIZE + len(rootfs)
    if rootfs_end != metadata_offset:
        raise SystemExit(
            "Rootfs UBI does not end at the template metadata boundary: "
            f"0x{rootfs_end:x} != 0x{metadata_offset:x}"
        )

    bank = bytearray(template)
    bank[:KERNEL_SIZE] = kernel
    bank[KERNEL_SIZE:rootfs_end] = rootfs
    if len(bank) != BANK_SIZE:
        raise SystemExit("Internal bank-size verification failed")
    args.output.write_bytes(bank)

    print(f"Template SHA-256: {digest(template)}")
    print(f"Kernel SHA-256: {digest(kernel)}")
    print(f"Rootfs SHA-256: {digest(rootfs)}")
    print(f"Bank SHA-256:   {digest(bank)}")
    print(f"Bank size:      {len(bank)} bytes")


if __name__ == "__main__":
    main()

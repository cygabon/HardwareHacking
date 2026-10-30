#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Disable the activation timer in one verified tri_sdk_l2.ko build."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path


EXPECTED_SHA256 = "47571d7c90d551b18e72fa1a2d64ffa8f116f0b5c82d426ae06bac2275ac0ceb"
PATCHED_SHA256 = "d6481306e9a03df759894f0fa0110993371fac8531e42237758a1abfaf39895a"
PATCH_OFFSET = 0xE50
EXPECTED_BYTES = bytes.fromhex("10402de9")  # push {r4, lr}
PATCHED_BYTES = bytes.fromhex("1eff2fe1")  # bx lr


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Patch a verified TGP 3.3.4 tri_sdk_l2.ko module"
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    source = args.input.read_bytes()
    digest = sha256(source)
    if digest == PATCHED_SHA256:
        raise SystemExit("Input is already the supported patched module")
    if digest != EXPECTED_SHA256:
        raise SystemExit(
            f"Unsupported input SHA-256: {digest}\nExpected: {EXPECTED_SHA256}"
        )
    found = source[PATCH_OFFSET : PATCH_OFFSET + len(EXPECTED_BYTES)]
    if found != EXPECTED_BYTES:
        raise SystemExit(
            f"Unexpected bytes at 0x{PATCH_OFFSET:x}: {found.hex()}"
        )

    patched = bytearray(source)
    patched[PATCH_OFFSET : PATCH_OFFSET + len(PATCHED_BYTES)] = PATCHED_BYTES
    output_digest = sha256(patched)
    if output_digest != PATCHED_SHA256:
        raise SystemExit(f"Internal verification failed: {output_digest}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(patched)
    os.chmod(args.output, args.input.stat().st_mode & 0o777)
    changed = [
        index
        for index, pair in enumerate(zip(source, patched))
        if pair[0] != pair[1]
    ]
    print(f"Input SHA-256:  {digest}")
    print(f"Output SHA-256: {output_digest}")
    print(f"Changed bytes:   {len(changed)} at {[hex(index) for index in changed]}")


if __name__ == "__main__":
    main()

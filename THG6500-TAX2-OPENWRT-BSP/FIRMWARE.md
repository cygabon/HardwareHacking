# Firmware patch and A/B deployment

Writing NAND can brick the router. Keep a working 3.3 V UART console and two
verified backups of every MTD partition. Never write `uboot`, `equip`, `wlanrf`,
factory or calibration partitions.

## 1. Patch the verified module

Copy the module from your own firmware or read-only root filesystem:

```sh
scp -O root@ROUTER_IP:/rom/lib/modules/5.10.138/tri_sdk_l2.ko .
sha256sum tri_sdk_l2.ko
python3 scripts/patch_tri_sdk_l2.py \
  tri_sdk_l2.ko tri_sdk_l2.patched.ko
```

Supported hashes:

| Artifact | SHA-256 |
|---|---|
| Original module | `47571d7c90d551b18e72fa1a2d64ffa8f116f0b5c82d426ae06bac2275ac0ceb` |
| Patched module | `d6481306e9a03df759894f0fa0110993371fac8531e42237758a1abfaf39895a` |

The patch changes four bytes at file offset `0xe50`:

```text
10 40 2d e9    push {r4, lr}
1e ff 2f e1    bx lr
```

## 2. Rebuild the root filesystem

Replacing `/lib/modules/...` in the writable overlay is ineffective: this
module is loaded from `/rom` before the overlay is available. Replace it in an
extracted root filesystem and reproduce the original image geometry.

The tested firmware used:

- SquashFS 4.0, XZ preset 9, ARM BCJ, 256 KiB blocks;
- UBI PEB 128 KiB, minimum I/O 2 KiB, sub-page 2 KiB;
- dynamic UBI volume ID 0 named `rootfs`;
- an 8 MiB kernel slot followed by a 32 MiB rootfs slot.

Example SquashFS command using the matching BSP host tool:

```sh
sudo /path/to/BSP/staging_dir/host/bin/mksquashfs4 \
  rootfs rootfs-patched.squashfs \
  -noappend -comp xz -Xbcj arm -b 262144
```

Example `ubinize.cfg`; set `vol_size` to the rebuilt SquashFS size rounded up
to 1 KiB:

```ini
[rootfs]
mode=ubi
vol_id=0
vol_type=dynamic
vol_name=rootfs
image=rootfs-patched.squashfs
vol_size=SIZE_ROUNDED_UP_TO_1024
```

```sh
ubinize -o rootfs-patched.ubi -p 128KiB -m 2048 -s 2048 ubinize.cfg
python3 scripts/assemble_firmware_bank.py \
  firmware-inactive-original.bin kernel-inactive.bin \
  rootfs-patched.ubi firmware-inactive-patched.bin
```

The assembler preserves the vendor metadata and padding from your original
inactive-bank image. It refuses an image unless the rebuilt UBI ends exactly at
the original metadata boundary.

Re-detect every geometry value from your own image. Do not assume all firmware
revisions use the tested layout.

## 3. Deploy only to the inactive bank

1. Check `/proc/mtd` and `/etc/upgflag get active`.
2. Resolve the inactive enclosing `firmwareA` or `firmwareB` partition by name,
   never by a hard-coded `/dev/mtdN` number.
3. Write only that inactive bank.
4. Run the platform `mtd verify` operation and compare a complete read-back
   SHA-256 before switching banks.
5. Switch with `/etc/upgflag switch` and watch the entire boot over UART.

After boot, both module paths must have the patched hash:

```sh
sha256sum /rom/lib/modules/5.10.138/tri_sdk_l2.ko
sha256sum /lib/modules/5.10.138/tri_sdk_l2.ko
```

Keep the original bank untouched. On a successful Linux boot,
`/etc/upgflag switch` provides the rollback path.

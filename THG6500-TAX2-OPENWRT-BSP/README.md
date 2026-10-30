# THG6500-TAX2 OpenWrt BSP research

Reverse-engineering notes and a reproducible stability patch for the Banana Pi
BPI-WiFi6 Router / THG6500-TAX2, target `tr6560/generic`, Linux 5.10.138.

## Upstream sources

This repository does not mirror the vendor BSP or firmware:

- [Banana Pi device documentation](https://docs.banana-pi.org/en/BPI-WiFi6_Router/BananaPi_BPI-WiFi6_Router)
- [Original THG6500-TAX2 OpenWrt BSP](https://github.com/BPI-SINOVOIP/THG6500-TAX2-OPENWRT-BSP)
- [TGP3 BSP](https://github.com/BPI-SINOVOIP/THG6500-TAX2-OPENWRT-BSP_TGP3)

## Problem

One TGP 3.3.4 firmware build periodically reports an activation-key mismatch
and deliberately reboots after approximately 3,651 seconds:

```text
MAC and KEY are mismatched
no activation! reboot!
```

The reboot comes from the proprietary `tri_sdk_l2.ko` module. Its
`tri_shield_check` callback rearms a three-second timer, limits Wi-Fi after
repeated failures, and eventually invokes the platform restart routine.

## Patch

The supplied tool changes one verified ARM instruction so the callback returns
before rearming the timer or modifying Wi-Fi state. It accepts only the exact
module hash that was analyzed.

```sh
python3 scripts/patch_tri_sdk_l2.py tri_sdk_l2.ko tri_sdk_l2.patched.ko
```

See [FIRMWARE.md](FIRMWARE.md) for extraction, rebuild and A/B deployment, and
[RESULTS.md](RESULTS.md) for measured results.

## Publication policy

No firmware image, flash dump, calibration data, MAC address, serial number,
activation key, password or router configuration is included. Use these tools
only on hardware you own or are authorized to test.

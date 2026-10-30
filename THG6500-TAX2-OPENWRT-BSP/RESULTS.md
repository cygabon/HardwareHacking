# Results

Test date: 2026-10-30. Device: THG6500-TAX2, TGP 3.3.4, Linux 5.10.138.

## Original firmware

- activation warnings observed at approximately 303.925 and 607.925 seconds;
- UART message `no activation! reboot!` at 3,650.965 seconds;
- Ethernet and Wi-Fi dropped together during the deliberate reboot;
- service returned only after the complete boot sequence.

## Patched bank B

- patched module loaded from `/rom`, not from an overlay;
- `/rom` and visible module SHA-256:
  `d6481306e9a03df759894f0fa0110993371fac8531e42237758a1abfaf39895a`;
- no activation warning at either original warning deadline;
- activation counter remained zero;
- bank A remained original and available for rollback;
- validation was still running at 2,692 seconds when this interim result was
  published. Final validation requires passing the old 3,651-second deadline.

Rebuilt artifact hashes from the tested unit are provided for reproducibility,
but the proprietary artifacts themselves are not distributed:

| Artifact | SHA-256 |
|---|---|
| SquashFS rootfs | `3d91c352c9db0f2b5dd19e2d3b65bb2e4baed985b27420ef73af5075eadcd52a` |
| Rootfs UBI | `dc7a71834db5010d86449af8883ebbcf932a708e4c16a159323d64c1b20e6ad5` |
| 40 MiB bank image | `3ad0cc5210e7f60831a2f8adc61631dc82c5d81ece5886c25761ce2228324eae` |

## Separate Wi-Fi observation

Short Wi-Fi-only packet losses still occurred while Ethernet and router uptime
remained stable. A 200 ms dual-path probe captured two Wi-Fi misses and zero
Ethernet misses over its first 6,500 paired samples. These events are distinct
from the activation reboot and remain a separate radio/driver investigation.

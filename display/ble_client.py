"""BLE client that listens for category-select notifications from the ESP32.

The ESP32 firmware exposes a characteristic with PROPERTY_NOTIFY whose value is
a JSON payload like {"category":"scientist"}. Each button press triggers one
notify; we forward valid categories to the server's event queue when the
mirror is in the category_select state.
"""

import asyncio
import json
import time

import server


DEVICE_NAME = "ESP32 Selector"
ADDRESS = "8E6AA1FA-3B99-4A4D-BC3E-ADFB34EC55D6"
CHAR_UUID = "abcd1234-ab12-ab12-ab12-abcdef123456"
VALID = {"scientist", "engineer", "entrepreneur"}

SCAN_TIMEOUT_S = 10.0
RESCAN_BACKOFF_S = 5.0
DISCONNECT_BACKOFF_S = 2.0


def run() -> None:
    """Daemon-thread entrypoint: spins up an asyncio loop and runs _main()."""
    try:
        asyncio.run(_main())
    except Exception as exc:
        server.write_perf_log("ble_thread_crash", error=str(exc))
        print(f"ble_client: thread exiting due to {exc}")


async def _main() -> None:
    try:
        from bleak import BleakClient, BleakScanner
        from bleak.exc import BleakError
    except ImportError:
        print("ble_client: bleak unavailable, BLE disabled")
        server.write_perf_log("ble_disabled", reason="bleak_not_installed")
        return

    server.write_perf_log("ble_started")
    POLL_INTERVAL = 0.2  # 5 Hz

    while True:
        try:
            device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=SCAN_TIMEOUT_S)
            if device is None:
                await asyncio.sleep(RESCAN_BACKOFF_S)
                continue

            async with BleakClient(device) as client:
                server.write_perf_log("ble_connected", address=str(device.address))

                baseline: str | None = None
                last_state: str = ""

                while client.is_connected:
                    state, _ = server.get_state_snapshot()

                    # On entering category_select, snapshot current value as baseline.
                    if state == "category_select" and last_state != "category_select":
                        try:
                            raw = await client.read_gatt_char(CHAR_UUID)
                            baseline = _parse_category(raw)
                        except Exception:
                            baseline = None
                        server.write_perf_log("ble_baseline_set", baseline=baseline)
                    last_state = state

                    if state == "category_select":
                        try:
                            raw = await client.read_gatt_char(CHAR_UUID)
                            cat = _parse_category(raw)
                        except Exception:
                            cat = None

                        if cat in VALID and cat != baseline:
                            server.set_selected_category(cat)
                            server.enqueue_event(
                                {"type": "category_selected", "category": cat},
                                source="ble_client",
                            )
                            baseline = cat  # prevent re-fire on next poll

                    await asyncio.sleep(POLL_INTERVAL)

        except BleakError as exc:
            server.write_perf_log("ble_error", error=str(exc))
            await asyncio.sleep(DISCONNECT_BACKOFF_S)
        except Exception as exc:
            server.write_perf_log("ble_loop_exception", error=str(exc))
            await asyncio.sleep(DISCONNECT_BACKOFF_S)


def _parse_category(data: bytearray | bytes) -> str | None:
    try:
        obj = json.loads(bytes(data).decode("utf-8").strip())
        return obj.get("category")
    except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        return None

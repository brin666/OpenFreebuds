"""Probe a paired HUAWEI FreeBuds 7i using OpenFreebuds' FreeBuds 6i battery request.

Run from this repository on Windows with:
    python freebuds7i_probe.py

Only reads the paired-device registry entry, opens RFCOMM channel 1, sends one
battery read request, prints all received bytes, then tries OpenFreebuds' own
Huawei SPP package and battery handler. It does not change pairing or settings.
"""

from __future__ import annotations

import asyncio
import importlib
import socket
import sys
import time
import types
import winreg
from pathlib import Path
from typing import Any


REGISTRY_DEVICES = r"SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Devices"
DEVICE_NAME_VALUES = ("Name", "LEName")
TARGET_NAME = "freebuds7i"
SPP_CHANNEL = 1  # OpenFreebuds' FreeBuds 6i profile
RESPONSE_TIMEOUT = 4.0
QUIET_TIMEOUT = 0.4


def _decode_registry_name(raw: Any) -> str:
    if isinstance(raw, bytes):
        return raw.decode("utf-8", "replace").rstrip("\x00").strip()
    if isinstance(raw, str):
        try:
            decoded = bytes.fromhex(raw).decode("utf-8", "replace")
            if decoded.strip("\x00\r\n "):
                return decoded.rstrip("\x00").strip()
        except ValueError:
            pass
        return raw.rstrip("\x00").strip()
    return ""


def find_paired_7i() -> list[tuple[str, str]]:
    """Return matching (name, colon-separated address) pairs from Windows registry."""
    root = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REGISTRY_DEVICES)
    found: list[tuple[str, str]] = []
    try:
        index = 0
        while True:
            try:
                device_id = winreg.EnumKey(root, index)
            except OSError:
                break
            index += 1
            if len(device_id) != 12:
                continue

            device_key = None
            try:
                device_key = winreg.OpenKey(root, device_id)
                name = ""
                for value_name in DEVICE_NAME_VALUES:
                    try:
                        raw, _ = winreg.QueryValueEx(device_key, value_name)
                    except FileNotFoundError:
                        continue
                    name = _decode_registry_name(raw)
                    if name:
                        break
            except OSError:
                continue
            finally:
                if device_key is not None:
                    winreg.CloseKey(device_key)

            if TARGET_NAME in "".join(ch.lower() for ch in name if ch.isalnum()):
                address = ":".join(device_id[i : i + 2] for i in range(0, 12, 2)).upper()
                found.append((name, address))
    finally:
        winreg.CloseKey(root)
    return found


def load_openfreebuds_battery_parser():
    """Load the repo's package parser and battery handler without its UI/WinRT imports.

    OpenFreebuds' normal package initializers import the Windows WinRT backend.
    The probe only needs the actual SPP package and battery handler source files,
    so lightweight package stubs keep this script runnable as a standalone tool.
    """
    repo = Path(__file__).resolve().parent
    packages = {
        "openfreebuds": repo / "openfreebuds",
        "openfreebuds.driver": repo / "openfreebuds" / "driver",
        "openfreebuds.driver.huawei": repo / "openfreebuds" / "driver" / "huawei",
        "openfreebuds.driver.huawei.handler": repo / "openfreebuds" / "driver" / "huawei" / "handler",
        "openfreebuds.driver.huawei.driver": repo / "openfreebuds" / "driver" / "huawei" / "driver",
    }
    for name, directory in packages.items():
        module = types.ModuleType(name)
        module.__path__ = [str(directory)]  # type: ignore[attr-defined]
        module.__package__ = name
        sys.modules[name] = module

    # Avoid importing the real driver module, which pulls in Windows WinRT.
    driver_generic = types.ModuleType("openfreebuds.driver.huawei.driver.generic")
    driver_generic.OfbDriverHandlerHuawei = type("OfbDriverHandlerHuawei", (), {})
    sys.modules[driver_generic.__name__] = driver_generic

    battery_module = importlib.import_module("openfreebuds.driver.huawei.handler.battery")
    package_module = importlib.import_module("openfreebuds.driver.huawei.package")
    command_module = importlib.import_module("openfreebuds.driver.huawei.constants")
    return (
        battery_module.OfbHuaweiBatteryHandler,
        package_module.HuaweiSppPackage,
        command_module.CMD_BATTERY_READ,
    )


def _split_frames(raw: bytes) -> list[bytes]:
    """Split concatenated length-delimited OpenFreebuds Huawei SPP frames."""
    frames: list[bytes] = []
    position = 0
    while position + 4 <= len(raw):
        start = raw.find(b"\x5a", position)
        if start < 0 or start + 4 > len(raw):
            break
        length = int.from_bytes(raw[start + 1 : start + 3], "big")
        frame_size = length + 5  # header + declared body + CRC16
        if length < 4 or start + frame_size > len(raw):
            position = start + 1
            continue
        frames.append(raw[start : start + frame_size])
        position = start + frame_size
    return frames


def _print_battery(values: dict[str, Any] | None) -> None:
    values = values or {}
    print("Parsed:")
    print(f"  Left:  {values.get('left', 'unknown')}%" if "left" in values else "  Left:  unknown")
    print(f"  Right: {values.get('right', 'unknown')}%" if "right" in values else "  Right: unknown")
    print(f"  Case:  {values.get('case', 'unknown')}%" if "case" in values else "  Case:  unknown")


async def _parse_with_openfreebuds(frames: list[bytes]) -> None:
    BatteryHandler, HuaweiSppPackage, _ = load_openfreebuds_battery_parser()
    from openfreebuds.driver.huawei.utils import crc16_xmodem

    class BatteryCapture:
        battery: dict[str, Any] | None = None

        async def put_property(self, group, prop, value):
            if group == "battery" and prop is None:
                self.battery = value

    battery_values = None
    battery_frames = 0
    for index, frame in enumerate(frames, start=1):
        package = HuaweiSppPackage.from_bytes(frame)
        crc_ok = crc16_xmodem(frame[:-2]) == frame[-2:]
        print(
            f"Frame {index}: command {package.command_id.hex(' ').upper()}, "
            f"CRC16/XMODEM {'valid' if crc_ok else 'invalid'}"
        )
        if package.command_id != b"\x01\x08":
            continue
        battery_frames += 1
        capture = BatteryCapture()
        handler = BatteryHandler()
        handler.driver = capture
        await handler.on_package(package)
        battery_values = capture.battery

    if battery_frames == 0:
        print("No 01 08 battery response frame was found.")
    _print_battery(battery_values)


def run() -> int:
    if sys.platform != "win32":
        print("This probe requires Windows Bluetooth and the Windows paired-device registry.")
        return 2

    try:
        devices = find_paired_7i()
    except OSError as exc:
        print(f"Device discovery failed: {type(exc).__name__}: {exc}")
        return 2

    if not devices:
        print("No paired HUAWEI FreeBuds 7i found in the Windows Bluetooth registry.")
        print("Pair the earbuds in Windows Settings, then run this script again.")
        return 2

    if len(devices) > 1:
        for index, (name, address) in enumerate(devices, start=1):
            print(f"{index}. {name} — {address}")
        try:
            selected = int(input("Select the FreeBuds 7i to probe: ")) - 1
            name, address = devices[selected]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return 2
    else:
        name, address = devices[0]

    print("Device detected:")
    print(f"  {name}")
    print(f"Bluetooth Address: {address}")
    print("Profile: FreeBuds 6i battery-compatible (verified); other features untested")
    print(f"RFCOMM/SPP channel: {SPP_CHANNEL}")

    try:
        _, HuaweiSppPackage, battery_command = load_openfreebuds_battery_parser()
        request = HuaweiSppPackage.read_rq(battery_command, [1, 2, 3]).to_bytes()
    except Exception as exc:
        print(f"Could not prepare the OpenFreebuds 6i battery request: {type(exc).__name__}: {exc}")
        return 3

    print(f"TX HEX: {request.hex(' ').upper()}")
    raw = bytearray()
    sock = None
    try:
        if not hasattr(socket, "AF_BLUETOOTH") or not hasattr(socket, "BTPROTO_RFCOMM"):
            raise RuntimeError("This Python build does not expose Bluetooth RFCOMM sockets")
        sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        sock.settimeout(5.0)
        print("Connecting to RFCOMM channel 1...")
        sock.connect((address, SPP_CHANNEL))
        sock.sendall(request)
        end_at = time.monotonic() + RESPONSE_TIMEOUT
        while time.monotonic() < end_at:
            remaining = end_at - time.monotonic()
            sock.settimeout(min(0.5, remaining))
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                if raw:
                    break
                continue
            if not chunk:
                break
            raw.extend(chunk)
    except Exception as exc:
        print(f"RFCOMM/battery probe failed: {type(exc).__name__}: {exc}")
        return 4
    finally:
        if sock is not None:
            sock.close()

    if not raw:
        print("Battery packet: no response (0 bytes)")
        _print_battery(None)
        print("The FreeBuds 6i battery request was sent, but no compatible reply was received.")
        return 5

    print(f"Battery packet RAW HEX ({len(raw)} bytes): {bytes(raw).hex(' ').upper()}")
    frames = _split_frames(bytes(raw))
    if not frames:
        print("Could not find a complete OpenFreebuds Huawei SPP frame; full raw bytes are shown above.")
        _print_battery(None)
        return 6

    try:
        asyncio.run(_parse_with_openfreebuds(frames))
    except Exception as exc:
        print(f"FreeBuds 6i parser failed: {type(exc).__name__}: {exc}")
        _print_battery(None)
        return 7
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

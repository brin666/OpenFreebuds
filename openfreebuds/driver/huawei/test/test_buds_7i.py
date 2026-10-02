import asyncio

import pytest

from openfreebuds.driver.constants import DEVICE_TO_DRIVER_MAP
from openfreebuds.driver.huawei.driver.generic import OfbDriverHuaweiGeneric
from openfreebuds.driver.huawei.driver.per_model.buds_7i import OfbDriverHuawei7I
from openfreebuds.driver.huawei.handler import OfbHuaweiBatteryHandler
from openfreebuds.driver.huawei.package import HuaweiSppPackage


LIVE_BATTERY_RESPONSE = bytes.fromhex(
    "5a001b000108010132020332350103030000000402140a0502000006010a651b"
)
SHORT_NOTIFICATION = bytes.fromhex("5a00030001063ebd")
FOLLOWING_NOTIFICATION = bytes.fromhex(
    "5a001e002bac0101010201010301000401000501000601000701000801000901000988"
)


def test_freebuds_7i_maps_to_battery_only_port_1_profile():
    driver = OfbDriverHuawei7I("00:00:00:00:00:00")

    assert DEVICE_TO_DRIVER_MAP["HUAWEI FreeBuds 7i"] is OfbDriverHuawei7I
    assert driver._spp_service_port == 1
    assert len(driver.handlers) == 1
    assert isinstance(driver.handlers[0], OfbHuaweiBatteryHandler)


@pytest.mark.asyncio
async def test_freebuds_7i_battery_response_maps_left_right_and_case():
    package = HuaweiSppPackage.from_bytes(LIVE_BATTERY_RESPONSE, validate_checksum=True)
    handler = OfbHuaweiBatteryHandler()
    properties = {}

    class Driver:
        async def put_property(self, key, index, value):
            properties[key] = value

    handler.driver = Driver()
    await handler.on_package(package)

    assert properties["battery"]["left"] == 50
    assert properties["battery"]["right"] == 53
    assert properties["battery"]["case"] == 1


@pytest.mark.asyncio
async def test_receiver_consumes_short_frame_crc_before_following_frames():
    driver = OfbDriverHuaweiGeneric.__new__(OfbDriverHuaweiGeneric)
    received = []

    async def record_package(package):
        received.append(package)

    driver._handle_raw_pkg = record_package
    reader = asyncio.StreamReader()
    reader.feed_data(
        SHORT_NOTIFICATION
        + LIVE_BATTERY_RESPONSE
        + SHORT_NOTIFICATION
        + FOLLOWING_NOTIFICATION
    )
    reader.feed_eof()

    await driver._OfbDriverHuaweiGeneric__recv_pacakge(reader)
    await driver._OfbDriverHuaweiGeneric__recv_pacakge(reader)
    await driver._OfbDriverHuaweiGeneric__recv_pacakge(reader)
    await driver._OfbDriverHuaweiGeneric__recv_pacakge(reader)

    assert received == [LIVE_BATTERY_RESPONSE, FOLLOWING_NOTIFICATION]

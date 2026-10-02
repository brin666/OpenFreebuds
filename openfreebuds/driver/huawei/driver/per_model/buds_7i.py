from openfreebuds.driver.huawei.driver.generic import OfbDriverHuaweiGeneric
from openfreebuds.driver.huawei.handler import OfbHuaweiBatteryHandler


class OfbDriverHuawei7I(OfbDriverHuaweiGeneric):
    """Battery-only SPP profile for HUAWEI FreeBuds 7i."""

    def __init__(self, address):
        super().__init__(address)
        self._spp_service_port = 1
        self.handlers = [OfbHuaweiBatteryHandler()]

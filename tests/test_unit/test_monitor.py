import sys
from typing import Dict, Optional, Union

from aiomon.monitor import Monitor, MonitorData, MonitorOutput

# TODO: maybe make included JSONMonitorData with Dict/List that serializable
KVMonitorDataValue = Union[str, int, float]


class KVMonitorData:
    def __init__(self) -> None:
        self.__data: Dict[str, KVMonitorDataValue] = {}

    async def get_value(self, key: str) -> Optional[KVMonitorDataValue]:
        return self.__data.get(key)

    async def set_value(self, key: str, value: KVMonitorDataValue) -> None:
        self.__data[key] = value

    async def delete_value(self, key: str) -> None:
        del self.__data[key]


class KVStdErrMonitorOutput:
    async def write(self, data: KVMonitorData) -> None:
        sys.stderr.write(str(data))
        sys.stderr.flush()


async def test_kv_monitor_output_is_valid_impl_of_protocol():
    monitor_output = KVStdErrMonitorOutput()
    assert isinstance(monitor_output, MonitorOutput)


async def test_kv_monitor_data_is_valid_impl_of_protocol():
    monitor_data = KVMonitorData()
    assert isinstance(monitor_data, MonitorData)


async def test_kv_monitor_data_methods_work():
    monitor_data = KVMonitorData()
    assert await monitor_data.set_value("key", "value") is None
    assert await monitor_data.get_value("key") == "value"
    assert await monitor_data.set_value("key", 1) is None
    assert await monitor_data.get_value("key") == 1
    assert await monitor_data.set_value("key", 1.0) is None
    assert await monitor_data.get_value("key") == 1.0
    assert await monitor_data.delete_value("key") is None
    assert await monitor_data.get_value("key") is None


async def test_not_implementing_protocol_monitor_data_is_not_valid():
    class InvalidKVMonitorData:
        def __init__(self) -> None:
            self.__data: Dict[str, KVMonitorDataValue] = {}

        async def get_value(self, key: str) -> Optional[KVMonitorDataValue]:
            return self.__data.get(key)

        async def set_value(self, key: str, value: KVMonitorDataValue) -> None:
            self.__data[key] = value

    monitor_data = InvalidKVMonitorData()
    assert not isinstance(monitor_data, MonitorData)


async def test_using_correct_protocol_impls_in_monitor_works():
    monitor = Monitor[str, KVMonitorDataValue](
        name="test-monitor",
        cls_data=KVMonitorData,
        cls_output=KVStdErrMonitorOutput,
    )
    assert await monitor.get_value("key") is None
    assert await monitor.set_value("key", "value") is None
    assert await monitor.get_value("key") == "value"
    assert await monitor.delete_value("key") is None
    assert await monitor.get_value("key") is None

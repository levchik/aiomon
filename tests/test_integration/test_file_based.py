# class HealthMonitorData(MonitorData[str, bool]):
#     def __init__(self) -> None:
#         self.__data = {}
#
#     async def get(self, key: str) -> bool:
#         return self.__data.get(key, False)
#
#     async def set(self, key: str, value: bool) -> None:
#         self.__data[key] = value
#
#     async def update(self, key: str, value: bool) -> None:
#         self.__data[key] = value
#
#     async def delete(self, key: str) -> None:
#         del self.__data[key]
#
#     def raw(self) -> Dict[str, bool]:
#         return self.__data
#
#
# class JSONFileMonitorOutput(MonitorOutput):
#     filename = ".health.json"
#
#     async def write(self, data: HealthMonitorData) -> None:
#         # Save data to disk
#         with open(self.filename, "w") as f:
#             # Could be in json so that some tool like jq could read
#             f.write(json.dumps(data.raw()))
#
#
# async def run_app(monitor: Monitor):
#     print("Running app")
#     await asyncio.sleep(5)
#     await monitor.set("healthy", False)
#     await asyncio.sleep(5)
#     await monitor.set("healthy", True)
#     await asyncio.sleep(5)
#     print("App is closed, Bye!")
#
#
# async def main():
#     health_monitor = Monitor(
#         "health",
#         cls_data=HealthMonitorData,
#         cls_output=JSONFileMonitorOutput
#     )
#     await run_app(monitor=health_monitor)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())

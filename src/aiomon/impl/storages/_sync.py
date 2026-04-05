import contextlib
from typing import (
    AsyncGenerator,
    Generic,
    TypeVar,
)

import aiorwlock  # type: ignore

T = TypeVar("T")


class RWMutex(Generic[T]):
    """
    Read-Write Mutex generic over the value it stores.
    """

    def __init__(self, value: T):
        """
        Lock is safe by default, but we have context switches
        (await, async with, async for statements) inside locked code,
        so we use fast=True for minor speedup.
        """
        self.__value = value
        self.__lock = aiorwlock.RWLock(fast=True)

    @contextlib.asynccontextmanager
    async def writer_lock(self) -> AsyncGenerator[T, None]:
        """
        Writer lock only locks the mutex for everything, only one coroutine
        can hold the lock at any given time.
        It provides the protected value, and then unlocks the mutex when the
        context manager ends.
        """
        await self.__lock.writer.acquire()
        try:
            yield self.__value
        finally:
            self.__lock.writer.release()

    @contextlib.asynccontextmanager
    async def reader_lock(self) -> AsyncGenerator[T, None]:
        """
        Reader lock locks the mutex for read-only everything, many coroutines
        are allowed to hold the lock.
        It provides the protected value, and then unlocks the mutex when the
        context manager ends.
        """
        await self.__lock.reader.acquire()
        try:
            yield self.__value
        finally:
            self.__lock.reader.release()

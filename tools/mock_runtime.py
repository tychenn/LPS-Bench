"""Per-module in-memory state and deterministic clock for benchmark mock tools.

The runner imports each case module under a fresh name. Its tools can therefore
share simulated state within one case without reading or changing host files.
"""

from __future__ import annotations

import datetime as real_datetime
import hashlib
import io
import os as real_os
import posixpath
import random as real_random
import time as real_time
import types
import uuid as real_uuid

EPOCH = 1_790_380_800.0  # 2026-09-26 00:00:00 UTC


def stable_hash(value) -> int:
    """Return a repeatable mock identifier without Python's process hash seed."""
    digest = hashlib.sha256(repr(value).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


class _VirtualFile(io.BytesIO):
    def __init__(self, filesystem, path: str, mode: str, initial: bytes):
        super().__init__(initial)
        self._filesystem = filesystem
        self._path = path
        self._write_back = any(flag in mode for flag in "wax+")
        if "a" in mode:
            self.seek(0, io.SEEK_END)
        else:
            self.seek(0)

    def close(self):
        if not self.closed and self._write_back:
            self._filesystem.files[self._path] = self.getvalue()
        super().close()


class _VirtualTextFile(io.StringIO):
    def __init__(self, filesystem, path: str, mode: str, initial: str):
        super().__init__(initial)
        self._filesystem = filesystem
        self._path = path
        self._write_back = any(flag in mode for flag in "wax+")
        if "a" in mode:
            self.seek(0, io.SEEK_END)
        else:
            self.seek(0)

    def close(self):
        if not self.closed and self._write_back:
            self._filesystem.files[self._path] = self.getvalue().encode("utf-8")
        super().close()


class _VirtualFS:
    def __init__(self):
        self.files: dict[str, bytes] = {}
        self.directories: set[str] = {"/"}

    def path(self, raw_path) -> str:
        raw = real_os.fspath(raw_path).replace("\\", "/")
        if ".." in raw.split("/"):
            raise ValueError(f"Mock path traverses out of its virtual root: {raw}")
        return posixpath.normpath("/" + raw.lstrip("/"))

    def exists(self, raw_path) -> bool:
        path = self.path(raw_path)
        return path in self.files or path in self.directories

    def is_dir(self, raw_path) -> bool:
        return self.path(raw_path) in self.directories

    def is_file(self, raw_path) -> bool:
        return self.path(raw_path) in self.files

    def mkdir(self, raw_path, parents=False, exist_ok=False):
        path = self.path(raw_path)
        if path in self.files:
            raise FileExistsError(path)
        if path in self.directories:
            if not exist_ok:
                raise FileExistsError(path)
            return
        parent = posixpath.dirname(path)
        if parent not in self.directories:
            if not parents:
                raise FileNotFoundError(parent)
            self.mkdir(parent, parents=True, exist_ok=True)
        self.directories.add(path)

    def listdir(self, raw_path):
        path = self.path(raw_path)
        if path not in self.directories:
            raise FileNotFoundError(path)
        children = set()
        for entry in self.directories | self.files.keys():
            if entry != path and posixpath.dirname(entry) == path:
                children.add(posixpath.basename(entry))
        return sorted(children)

    def remove(self, raw_path):
        path = self.path(raw_path)
        if path not in self.files:
            raise FileNotFoundError(path)
        del self.files[path]

    def rmtree(self, raw_path):
        path = self.path(raw_path)
        if path == "/" or path not in self.directories:
            raise FileNotFoundError(path)
        prefix = path + "/"
        self.files = {name: data for name, data in self.files.items() if name != path and not name.startswith(prefix)}
        self.directories = {name for name in self.directories if name != path and not name.startswith(prefix)}

    def rename(self, raw_source, raw_destination):
        source, destination = self.path(raw_source), self.path(raw_destination)
        if destination in self.directories:
            destination = posixpath.join(destination, posixpath.basename(source))
        if source in self.files:
            self.files[destination] = self.files.pop(source)
            return
        if source not in self.directories:
            raise FileNotFoundError(source)
        self.mkdir(destination, parents=True, exist_ok=True)
        prefix = source + "/"
        for name in list(self.files):
            if name.startswith(prefix):
                self.files[destination + name[len(source):]] = self.files.pop(name)
        for name in list(self.directories):
            if name.startswith(prefix):
                self.directories.add(destination + name[len(source):])
                self.directories.remove(name)
        self.directories.remove(source)

    def copy(self, raw_source, raw_destination):
        source, destination = self.path(raw_source), self.path(raw_destination)
        if source not in self.files:
            raise FileNotFoundError(source)
        if destination in self.directories:
            destination = posixpath.join(destination, posixpath.basename(source))
        self.mkdir(posixpath.dirname(destination), parents=True, exist_ok=True)
        self.files[destination] = self.files[source]

    def open(self, raw_path, mode="r", *args, **kwargs):
        path = self.path(raw_path)
        if "x" in mode and path in self.files:
            raise FileExistsError(path)
        if "r" in mode and path not in self.files:
            raise FileNotFoundError(path)
        if any(flag in mode for flag in "wax"):
            self.mkdir(posixpath.dirname(path), parents=True, exist_ok=True)
        initial = b"" if "w" in mode or "x" in mode else self.files.get(path, b"")
        if "b" in mode:
            return _VirtualFile(self, path, mode, initial)
        return _VirtualTextFile(self, path, mode, initial.decode(kwargs.get("encoding") or "utf-8"))


class _PathProxy:
    join = staticmethod(real_os.path.join)
    dirname = staticmethod(real_os.path.dirname)
    basename = staticmethod(real_os.path.basename)
    normpath = staticmethod(real_os.path.normpath)

    def __init__(self, filesystem: _VirtualFS):
        self._filesystem = filesystem

    def exists(self, path):
        return self._filesystem.exists(path)

    def isdir(self, path):
        return self._filesystem.is_dir(path)

    def isfile(self, path):
        return self._filesystem.is_file(path)

    def islink(self, path):
        return False

    def getmtime(self, path):
        if not self.exists(path):
            raise FileNotFoundError(path)
        return EPOCH


class _OSProxy:
    def __init__(self, filesystem: _VirtualFS):
        self._filesystem = filesystem
        self.path = _PathProxy(filesystem)

    def makedirs(self, path, exist_ok=False):
        self._filesystem.mkdir(path, parents=True, exist_ok=exist_ok)

    def mkdir(self, path):
        self._filesystem.mkdir(path)

    def listdir(self, path):
        return self._filesystem.listdir(path)

    def remove(self, path):
        self._filesystem.remove(path)

    unlink = remove

    def rename(self, source, destination):
        self._filesystem.rename(source, destination)

    def stat(self, path):
        if not self._filesystem.exists(path):
            raise FileNotFoundError(path)
        size = len(self._filesystem.files.get(self._filesystem.path(path), b""))
        return types.SimpleNamespace(st_size=size, st_ino=1, st_mtime=EPOCH)

    def utime(self, path, times=None):
        if not self._filesystem.exists(path):
            raise FileNotFoundError(path)


class _ShutilProxy:
    def __init__(self, filesystem: _VirtualFS):
        self._filesystem = filesystem

    def rmtree(self, path):
        self._filesystem.rmtree(path)

    def move(self, source, destination):
        self._filesystem.rename(source, destination)
        return real_os.fspath(destination)

    def copy2(self, source, destination):
        self._filesystem.copy(source, destination)
        return real_os.fspath(destination)


class _Clock:
    def __init__(self):
        self._now = EPOCH

    def sleep(self, seconds):
        self._now += max(0.0, float(seconds))

    def time(self):
        self._now += 0.001
        return self._now

    def strftime(self, format_string, time_tuple=None):
        return real_time.strftime(format_string, time_tuple or real_time.gmtime(self.time()))


def bind(module_name: str):
    """Return isolated stand-ins for open, os, shutil, random, and time."""
    filesystem = _VirtualFS()
    return filesystem.open, _OSProxy(filesystem), _ShutilProxy(filesystem), real_random.Random(0), _Clock()


def bind_determinism(module):
    """Give one freshly loaded mock module repeatable IDs, time, and delays."""
    rng = real_random.Random(0)
    clock = _Clock()
    module.hash = stable_hash
    if isinstance(getattr(module, "random", None), types.ModuleType):
        module.random = rng
    if isinstance(getattr(module, "time", None), types.ModuleType):
        module.time = clock
    if isinstance(getattr(module, "uuid", None), types.ModuleType):
        module.uuid = types.SimpleNamespace(
            uuid4=lambda: real_uuid.UUID(int=rng.getrandbits(128), version=4)
        )

    class FixedDateTime(real_datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            value = cls.fromtimestamp(clock.time(), tz=real_datetime.timezone.utc)
            return value.astimezone(tz) if tz else value.replace(tzinfo=None)

        @classmethod
        def utcnow(cls):
            return cls.fromtimestamp(clock.time(), tz=real_datetime.timezone.utc).replace(tzinfo=None)

    class FixedDate(real_datetime.date):
        @classmethod
        def today(cls):
            current = real_datetime.datetime.fromtimestamp(clock.time(), tz=real_datetime.timezone.utc)
            return cls(current.year, current.month, current.day)

    date_value = getattr(module, "datetime", None)
    if isinstance(date_value, types.ModuleType):
        module.datetime = types.SimpleNamespace(
            datetime=FixedDateTime,
            timedelta=real_datetime.timedelta,
            timezone=real_datetime.timezone,
            date=FixedDate,
        )
    elif date_value is real_datetime.datetime:
        module.datetime = FixedDateTime

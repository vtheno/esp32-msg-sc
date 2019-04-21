import struct
from binascii import hexlify, unhexlify
import sys
b2a_hex, a2b_hex = hexlify, unhexlify
from random import choice

_format = "<I64s"
_package_pack = struct.pack
_package_unpack = struct.unpack


def pack(length: int, id: str(64)) -> bytes:
    args = []
    args += [_format]
    args += [length]
    if sys.platform == "esp32":
        args += [id]
    else:
        args += [bytes(id, "utf8")]
    data = _package_pack(*args)
    return data


def unpack(data: bytes) -> dict:
    maps = {}
    maps["length"], *maps["id"] = _package_unpack(_format, data)
    maps["id"] = "".join(i.decode() for i in maps["id"])
    return maps


def data_unpack(data: bytes) -> str:
    data = data.decode()
    data = a2b_hex(data)
    return data.decode()


def data_pack(message: str) -> bytes:
    data = message.encode()
    data = b2a_hex(data)
    return len(data), data


_bases = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789=/"
_size = [0] * 64


def id_generate():
    while 1:
        yield "".join(choice(_bases) for _ in _size)


id_iter = id_generate()


def auto_pack(message: str) -> (bytes, bytes):
    id = next(id_iter)
    length, data = data_pack(message)
    return id, pack(length, id), data


__all__ = [
    "pack",
    "unpack",
    "data_pack",
    "data_unpack",
    "id_iter",
    "id_generate",
    "auto_pack",
]

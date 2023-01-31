import os
import re
import ctypes

from pyray import get_screen_height, get_screen_width


class Pointer:
    entity_list = 0x1A3520
    local_player = 0x1A3518
    view_matrix = 0x1B4FCC
    max_players = 0x1A352C


class Vec2(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float)
    ]


class Vec2_int(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_int),
        ("y", ctypes.c_int)
    ]


class Vec3(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('z', ctypes.c_float)
    ]


class Entity(ctypes.Structure):
    _fields_ = [
        ("", 0x8 * ctypes.c_byte),
        ("pos", Vec3),
        ("", 0xEC * ctypes.c_byte),
        ("health", ctypes.c_int32),
        ("", 0x115 * ctypes.c_byte),
        ("name", 0x32 * ctypes.c_char),
        ("", 0xD5 * ctypes.c_byte),
        ("team", ctypes.c_int32)
    ]


def world_to_screen(matrix, pos):
    clip = Vec3()
    ndc = Vec2()
    result = Vec2_int()

    clip.z = pos.x * matrix[3] + pos.y * matrix[7] + pos.z * matrix[11] + matrix[15]
    if clip.z < 0.2:
        raise IOError("WTS")
    clip.x = pos.x * matrix[0] + pos.y * matrix[4] + pos.z * matrix[8] + matrix[12]
    clip.y = pos.x * matrix[1] + pos.y * matrix[5] + pos.z * matrix[9] + matrix[13]
    ndc.x = clip.x / clip.z
    ndc.y = clip.y / clip.z
    result.x = int((get_screen_width() / 2 * ndc.x) + (ndc.x + get_screen_width() / 2))
    result.y = int(-(get_screen_height() / 2 * ndc.y) + (ndc.y + get_screen_height() / 2))
    return result


def get_window_info(name):
    info = os.popen(f"xwininfo -name {name}").read()
    regex = re.search(r"te upper-left X:\s\s(.+?)\n.+Y:\s\s(.+?)\n.+\n.+\n.+:\s(.+?)\n.+:\s(.+?)\n", info)
    return [int(i) for i in regex.groups()]
import memory
import helper

from ctypes import *
from pyray import *


class Entity:
    def __init__(self, mem, addr):
        self.data = mem.read(addr, helper.Entity(), False)
        self.color = RED if self.data.team == 0 else BLUE
        self.pos2d = None

    def draw_snapline(self):
        draw_line(get_screen_width() // 2, get_screen_height() // 2, self.pos2d.x, self.pos2d.y, self.color)

    def draw_name(self):
        offset = measure_text(self.data.name, 3) // 2
        draw_text(self.data.name, self.pos2d.x - offset, self.pos2d.y - 1, 3, WHITE)


def init():
    win = helper.get_window_info("AssaultCube")
    set_trace_log_level(5)
    set_target_fps(0)
    set_config_flags(ConfigFlags.FLAG_WINDOW_UNDECORATED)
    set_config_flags(ConfigFlags.FLAG_WINDOW_MOUSE_PASSTHROUGH)
    set_config_flags(ConfigFlags.FLAG_WINDOW_TRANSPARENT)
    set_config_flags(ConfigFlags.FLAG_WINDOW_TOPMOST)
    init_window(win[2], win[3], "AssaultCube ESP")
    set_window_position(win[0], win[1])


def main():
    mem = memory.Mem("linux_64_client")
    base = mem.module_base("linux_64_client")
    entity_list = mem.read(base + helper.Pointer.entity_list, c_int64())

    while not window_should_close():
        matrix = mem.read_array(base + helper.Pointer.view_matrix, c_float, 16)
        local_player_addr = mem.read(base + helper.Pointer.local_player, c_int64())
        max_players = mem.read(base + helper.Pointer.max_players, c_int32())

        begin_drawing()
        ent_array = mem.read_array(entity_list, c_int64, max_players * 8)
        for ent_addr in ent_array:
            if ent_addr != 0 and ent_addr != local_player_addr:
                try:
                    ent = Entity(mem, ent_addr)
                    if ent.data.health <= 0:
                        continue
                    ent.pos2d = helper.world_to_screen(matrix, ent.data.pos)
                    ent.draw_snapline()
                    ent.draw_name()
                except IOError:
                    continue

        draw_fps(0, 0)
        clear_background(BLANK)
        end_drawing()


if __name__ == "__main__":
    init()
    main()

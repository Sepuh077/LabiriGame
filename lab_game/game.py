import arcade
import arcade.gui
import random
from lab_generator import create_way
import math
import time

s_w, s_h = arcade.get_display_size()
ms = 2
turn_s = 1


BLACK = arcade.color.BLACK
WHITE = arcade.color.WHITE
GRAY = arcade.color.GRAY
RED = arcade.color.RED


class Portal(arcade.Sprite):
    def __init__(self):
        super(Portal, self).__init__()
        self.all_textures = []
        self.frame = 0
        self.scale = 0.4
        for i in range(1, 5):
            self.all_textures.append(arcade.load_texture(f"portal_{i}.png"))

        self.texture = self.all_textures[0]

    def update_animation(self, delta_time: float = 1/60):
        self.frame += 0.1
        self.texture = self.all_textures[int(self.frame) % 4]


class Button:
    def __init__(self, x, y, width, height, text, active_color, inactive_color, text_color, text_color_2):
        self.center_x = x
        self.center_y = y
        self.w = width
        self.h = height
        self.text = text
        self.active_c = active_color
        self.inactive_c = inactive_color
        self.text_color = text_color
        self.text_color_2 = text_color_2

    def draw(self, x, y):
        if self.center_x - self.w/2 < x < self.center_x + self.w/2 and \
                self.center_y - self.h/2 < y < self.center_y + self.h/2:
            color = self.active_c
            text_color = self.text_color_2
#            window.set_mouse_cursor(window.cursor_hand)
        else:
            color = self.inactive_c
            text_color = self.text_color
#            window.set_mouse_cursor(window.cursor_arrow)

        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.w, self.h, color)
        arcade.draw_text(self.text, self.center_x, self.center_y, text_color, 14, align="center", anchor_x="center",
                         anchor_y="center")
        arcade.draw_rectangle_outline(self.center_x, self.center_y, self.w, self.h, self.inactive_c, 10)

    def on_click(self, x, y):
        act = 0
        if self.center_x - self.w/2 < x < self.center_x + self.w/2 and \
                self.center_y - self.h/2 < y < self.center_y + self.h/2:
            act = 1

        return act


class Player(arcade.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.walk_textures = []
        self.stand_textures = []
        self.load_textures()
        self.frame = 0

    def update_animation(self, delta_time: float = 1/30):
        self.frame += 1
        if (self.change_x == 0 and self.change_y == 0) or window.game_win:
            self.texture = self.stand_textures[int(self.frame/10) % 2]
        else:
            self.texture = self.walk_textures[int(self.frame / 10) % 2]

    def load_textures(self):
        for i in range(1, 3):
            self.walk_textures.append(arcade.load_texture(f"player_walk_{i}.png"))
            self.stand_textures.append(arcade.load_texture(f"player_stand_{i}.png"))


class GameWindow(arcade.Window):
    def __init__(self):
        super(GameWindow, self).__init__(s_w, s_h, "Lab", True)
        self.player = None
        self.player_list = None

#        self.cursor_hand = self.get_system_mouse_cursor(window.CURSOR_HAND)
#        self.cursor_arrow = self.get_system_mouse_cursor(window.CURSOR_DEFAULT)

        self.wall_list = None
        self.portals = None
        self.start_portals = None
        self.size_w = None
        self.size_h = None
        self.maze_w = None
        self.maze_h = None
        self.maze = None
        self.physics_engine = None
        self.start_button = None
        self.pass_button = None
        self.quit_button = None
        self.right = None
        self.left = None
        self.bottom = None
        self.top = None
        self.portal = None
        self.start_portal = None
        self.move_up = False
        self.move_down = False
        self.game_start = False
        self.game_win = False
        self.lev_end = False
        self.level_start = False
        self.player_max_scale = 1
        self.level = 100
        self.mouse_x = 0
        self.mouse_y = 0
        self.show_map = False
        self.show_map_time = 0
        self.lev_start_time = 0
        self.lev_duration = 0

    def setup(self):
        arcade.set_background_color(arcade.color.WHITE)
        self.start_button = Button(s_w/2, s_h/2, 100, 100, "Start", WHITE, BLACK, WHITE, BLACK)
        self.pass_button = Button(s_w/5, s_h/5, 100, 100, "Next", WHITE, GRAY, WHITE, BLACK)
        self.quit_button = Button(s_w/2, s_h/3, 100, 100, "QUIT", WHITE, BLACK, WHITE, BLACK)
        self.game_start = False
        self.player = Player()
        self.player.center_x = s_w/2
        self.player.center_y = s_h/2
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.portal = Portal()
        self.start_portal = Portal()
        self.size_w = 225
        self.size_h = 225

    def load_level(self):
        arcade.set_background_color(BLACK)
        self.level += 1
        self.game_start = False
        self.show_map = True
        self.game_win = False
        self.lev_end = False
        self.level_start = False
        self.move_up = False
        self.move_down = False
        self.maze_w = 4 + self.level
        self.maze_h = 4 + self.level
        if self.maze_w > 50:
            self.maze_w = self.maze_h = 50
        self.size_w = 225
        self.size_h = 225
        self.start_portal.center_x = 1.5 * self.size_w
        self.player.center_x = 1.5 * self.size_w
        self.start_portal.center_y = 1.5 * self.size_h
        self.player.center_y = 1.5 * self.size_h
        self.portal.center_x = (self.maze_w + 0.5) * self.size_w
        self.portal.center_y = (self.maze_h + 0.5) * self.size_h
        self.wall_list = arcade.SpriteList()
        self.portals = arcade.SpriteList()
        self.start_portals = arcade.SpriteList()
        self.portals.append(self.portal)
        self.start_portals.append(self.start_portal)
        self.player.angle = 0
        self.player.change_y = 0
        self.player.change_x = 0
        self.player.change_angle = 4
        self.player.scale = 0.01
        self.maze = create_maze(self.maze_w, self.maze_h)
        self.setup_maze()
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.wall_list)
        self.show_map_time = time.time()
        self.lev_start_time = 0
        self.lev_duration = 0

    def setup_maze(self):
        self.wall_list = arcade.SpriteList()
        for i in range(self.maze_h + 2):
            for j in range(self.maze_w + 2):
                if self.maze[i][j] == 0:
                    wall = arcade.Sprite("wall.jpeg", self.size_w/225)
                    wall.center_x = self.size_w * i + self.size_w/2
                    wall.center_y = self.size_h * j + self.size_h/2
                    self.wall_list.append(wall)

    def draw_map(self):
        size = s_h/(self.maze_h + 2)
        for i in range(self.maze_h + 2):
            for j in range(self.maze_w + 2):
                if self.maze[i][j] == 0:
                    x = size * i + size/2 + s_w/2 - s_h/2
                    y = size * j + size/2
                    arcade.draw_rectangle_filled(x, y, size, size, GRAY)

        arcade.draw_circle_filled(size * (self.maze_h + 0.5) + s_w/2 - s_h/2, size * (self.maze_w + 0.5), size/10, RED)

    def on_draw(self):
        if self.show_map:
            self.draw_map()
            arcade.draw_text(str(int(4 - time.time() + self.show_map_time)), s_w/2, s_h/2, WHITE, s_h/5,
                             anchor_x="center", anchor_y="center")
        if self.level_start:
            self.start_portals.draw()
        if self.game_start:
            self.wall_list.draw()
            self.portals.draw()
            self.player_list.draw()

        if not self.show_map:
            self.draw_vision()
        if not self.game_start and not self.show_map:
            self.start_button.draw(self.mouse_x, self.mouse_y)

        if self.lev_end:
            self.pass_button.draw(self.mouse_x, self.mouse_y)

        if self.game_start:
            self.draw_info()
        
        if not self.show_map:
            self.quit_button.draw(self.mouse_x, self.mouse_y)

    def on_update(self, delta_time: float = 1/30):
        arcade.start_render()
        if self.show_map:
            if time.time() - self.show_map_time >= 2.95:
                self.game_start_after_show()
        if self.game_start:
            self.wall_list.update()
            if not self.lev_end:
                self.lev_duration += delta_time
                self.player_list.update_animation()
                self.player_list.update()
                if arcade.check_for_collision_with_list(self.player, self.portals).__len__() > 0 and not self.game_win:
                    self.pass_level()
                self.physics_engine.update()
            self.portals.update_animation()
            self.movement()
            self.button_movement()

        if self.game_win and not self.lev_end:
            self.player.scale -= 0.01
            self.player.change_x = (self.portal.center_x - self.player.center_x)/20
            self.player.change_y = (self.portal.center_y - self.player.center_y)/20
            if self.player.scale <= 0:
                self.lev_end = True
        elif self.level_start:
            self.start_portals.update_animation()
            self.player.scale += 1/180
            if self.player.scale >= self.player_max_scale:
                self.player.scale = self.player_max_scale
                self.level_start = False
                self.player.angle = 0
                self.player.change_angle = 0
        if self.lev_end:
            self.player.change_x = 0
            self.player.change_y = 0
            if self.pass_button.center_x < self.player.center_x + 0.45 * s_w:
                self.pass_button.center_x += 50
            else:
                self.pass_button.center_x = self.player.center_x + 0.45 * s_w

        self.cam_sides()

    def on_key_press(self, key, modifiers):
        if self.game_start and not self.game_win and not self.level_start:
            if key == arcade.key.UP:
                self.move_up = True
            if key == arcade.key.RIGHT:
                self.player.change_angle = -turn_s
            if key == arcade.key.LEFT:
                self.player.change_angle = turn_s

    def on_key_release(self, key, modifiers):
        if self.game_start and not self.game_win and not self.level_start:
            if key == arcade.key.UP:
                self.move_up = False
            if key == arcade.key.RIGHT or key == arcade.key.LEFT:
                self.player.change_angle = 0

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_x = x + self.player.center_x - s_w/2
        self.mouse_y = y + self.player.center_y - s_h/2

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if not self.game_start:
            act = self.start_button.on_click(self.mouse_x, self.mouse_y)
            if act == 1:
                self.load_level()
        if self.lev_end:
            act = self.pass_button.on_click(self.mouse_x, self.mouse_y)
            if act == 1:
                self.load_level()
        
        act = self.quit_button.on_click(self.mouse_x, self.mouse_y)
        if act == 1:
            arcade.finish_render()
            arcade.close_window()

    def cam_sides(self):
        if not self.show_map:
            self.left = self.player.center_x - s_w/2
            self.right = self.left + s_w
            self.bottom = self.player.center_y - s_h/2
            self.top = self.bottom + s_h
        else:
            self.left = self.bottom = 0
            self.right, self.top = s_w, s_h

        arcade.set_viewport(self.left, self.right, self.bottom, self.top)

    def draw_vision(self):
        transparent = 0
        for i in range(int(s_w/6), int(s_w), int(s_h/10)):
            x, y = self.player.center_x, self.player.center_y
            arcade.draw_circle_outline(x, y, i, (0, 0, 0, transparent), s_h/10)
            transparent += 100

    def movement(self):
        angle = self.player.angle * math.pi / 180
        if self.move_up:
            self.player.change_y = ms * math.cos(angle)
            self.player.change_x = ms * -math.sin(angle)
        else:
            self.player.change_y = 0
            self.player.change_x = 0

    def button_movement(self):
        self.quit_button.center_x = self.player.center_x + 0.45 * s_w
        self.quit_button.center_y = self.player.center_y - 0.45 * s_h

    def pass_level(self):
        self.game_win = True
        self.player.change_angle = 8
        self.pass_button.center_x = self.player.center_x - s_w * 0.55
        self.pass_button.center_y = self.player.center_y

    def game_start_after_show(self):
        self.show_map = False
        self.level_start = True
        self.game_start = True
        self.lev_duration = 0

    def draw_info(self):
        coord_x = self.player.center_x / self.size_w
        coord_y = self.player.center_y / self.size_h
        arcade.draw_text(f"{self.maze_w}x{self.maze_h}", self.left, self.top, WHITE, s_h/25,
                         anchor_x="left", anchor_y="top")
        arcade.draw_text("X:" + str(int(coord_x)), self.left, self.top - s_h/10,
                         WHITE, s_h/25, anchor_x="left", anchor_y="top")
        arcade.draw_text("Y:" + str(int(coord_y)), self.left, self.top - s_h/5,
                         WHITE, s_h/25, anchor_x="left", anchor_y="center")
        arcade.draw_text(str(int(self.lev_duration)), self.right - s_w/4, self.top - s_h / 20, WHITE, s_h / 25,
                         anchor_x="right", anchor_y="top")
        arcade.draw_text(f"Level {self.level}", self.right, self.top - s_h/5, WHITE, s_h/25,
                         anchor_x="right", anchor_y="top")
        if self.level < 20:
            text = "Easy"
        elif self.level < 40:
            text = "Medium"
        else:
            text = "Hard"

        arcade.draw_text(text, self.right - s_h/15, self.top - s_h/4, WHITE, s_h/40, anchor_x="right", anchor_y="top")


def create_maze(maze_w, maze_h):
    maze = []
    way = create_way(maze_w, maze_h)

    maze.append([0])

    for _ in range(maze_w + 1):
        maze[0].append(0)

    for i in range(maze_h):
        maze.append([0])
        for j in range(maze_w):
            if [j, i] in way or random.randint(0, 5) < 3:
                maze[i + 1].append(1)
            else:
                maze[i + 1].append(0)
        maze[i + 1].append(0)

    maze.append([0])
    for _ in range(maze_w + 1):
        maze[maze_h + 1].append(0)

    return maze


window = GameWindow()
window.setup()
arcade.set_window(window)
arcade.run()

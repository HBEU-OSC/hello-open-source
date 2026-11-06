# -*- coding: utf-8 -*-
"""
三蛇争霸 —— 三条不同颜色、不同 AI 策略的贪吃蛇自由竞技
  红蛇：贪心策略（直冲最近食物，不躲不避）
  绿蛇：BFS 寻路 + 最大空间规避（会思考的安全型）
  蓝蛇：惯性随机游走（爱直行，偶尔朝食物靠）

规则：
  · 蛇撞墙 / 撞自己 / 撞别的蛇 /吃缩短食物把自己吃没了 => 出局，底部面板显示"X色蛇出局：原因"
  · 场上只剩最后一条蛇 => 显示"X色蛇获胜！"，游戏结束
"""

import sys
import os
import random
from collections import deque
import pygame

# ==================== 基础配置 ====================
CELL     = 22
COLS     = 28
ROWS     = 20
PANEL_H  = 100
WIDTH    = COLS * CELL
HEIGHT   = ROWS * CELL + PANEL_H

FPS      = 60
STEP_MS  = 110
FOOD_NUM = 3
POISON_NUM = 3       #  新增：缩短食物数量

DIRS = {
    'up':    (0, -1),
    'down':  (0, 1),
    'left':  (-1, 0),
    'right': (1, 0),
}
OPPOSITE = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}

SNAKE_COLORS = {
    '红': (235, 72, 72),
    '绿': (72, 200, 96),
    '蓝': (82, 132, 240),
}

BG_COLOR   = (26, 28, 38)
GRID_COLOR = (40, 42, 56)
PANEL_BG   = (16, 17, 24)
FOOD_COLOR = (255, 214, 64)
POISON_COLOR = (220, 50, 180)     #  新增：品红：缩短食物

# ==================== 小工具 ====================
def in_bounds(p):
    return 0 <= p[0] < COLS and 0 <= p[1] < ROWS


def dir_from_delta(dx, dy):
    for name, (a, b) in DIRS.items():
        if a == dx and b == dy:
            return name
    return None


def build_blocked(game):
    blocked = set()
    for s in game.snakes:
        if not s.alive:
            continue
        for p in s.body[:-1]:
            blocked.add(p)
    return blocked


def flood_fill(start, blocked, limit=600):
    seen = {start}
    q = deque([start])
    while q and len(seen) < limit:
        cur = q.popleft()
        for dx, dy in DIRS.values():
            np_ = (cur[0] + dx, cur[1] + dy)
            if not in_bounds(np_) or np_ in seen or np_ in blocked:
                continue
            seen.add(np_)
            q.append(np_)
    return len(seen)


# ==================== 三种移动策略 ====================
def strategy_red(game, snake):
    """红蛇：纯贪心，朝最近的食物直线前进，从不考虑安全。"""
    head = snake.body[0]
    if not game.foods:
        return snake.direction

    target = min(game.foods, key=lambda f: abs(f[0] - head[0]) + abs(f[1] - head[1]))
    back = OPPOSITE[snake.direction]

    best_dir, best_dist = None, 10 ** 9
    for name, (dx, dy) in DIRS.items():
        if name == back:
            continue
        nx, ny = head[0] + dx, head[1] + dy
        d = abs(nx - target[0]) + abs(ny - target[1])
        if d < best_dist:
            best_dist, best_dir = d, name
    return best_dir or snake.direction


def strategy_green(game, snake):
    """绿蛇：BFS 找最近食物的路径；走不通时选活动空间最大的方向。"""
    head = snake.body[0]
    blocked = build_blocked(game)

    prev = {head: None}
    q = deque([head])
    target = None
    while q:
        cur = q.popleft()
        if cur in game.foods:
            target = cur
            break
        for dx, dy in DIRS.values():
            np_ = (cur[0] + dx, cur[1] + dy)
            if not in_bounds(np_) or np_ in prev or np_ in blocked:
                continue
            prev[np_] = cur
            q.append(np_)

    if target is not None:
        cur = target
        while prev[cur] != head:
            cur = prev[cur]
        return dir_from_delta(cur[0] - head[0], cur[1] - head[1])

    best, best_space = None, -1
    for name, (dx, dy) in DIRS.items():
        np_ = (head[0] + dx, head[1] + dy)
        if not in_bounds(np_) or np_ in blocked:
            continue
        space = flood_fill(np_, blocked)
        if space > best_space:
            best_space, best = space, name
    return best or snake.direction


def strategy_blue(game, snake):
    """蓝蛇：惯性随机游走，喜欢保持直行，偶尔朝食物凑一凑。"""
    head = snake.body[0]
    blocked = build_blocked(game)

    options = []
    for name, (dx, dy) in DIRS.items():
        np_ = (head[0] + dx, head[1] + dy)
        if in_bounds(np_) and np_ not in blocked:
            options.append(name)

    if not options:
        return snake.direction

    if snake.direction in options and random.random() < 0.85:
        return snake.direction

    if game.foods and random.random() < 0.5:
        target = min(game.foods,
                     key=lambda f: abs(f[0] - head[0]) + abs(f[1] - head[1]))
        options.sort(key=lambda n: abs(head[0] + DIRS[n][0] - target[0]) +
                                 abs(head[1] + DIRS[n][1] - target[1]))
        return options[0]

    return random.choice(options)


# ==================== 蛇 ====================
class Snake:
    def __init__(self, name, body, direction, strategy):
        self.name = name
        self.color = SNAKE_COLORS[name]
        self.body = [tuple(p) for p in body]
        self.direction = direction
        self.strategy = strategy
        self.alive = True
        self.death_reason = None


# ==================== 游戏主体 ====================
class Game:
    def __init__(self):
        self.snakes = [
            Snake('红', [(6, 6), (5, 6), (4, 6)], 'right', strategy_red),
            Snake('绿', [(COLS - 7, ROWS - 7), (COLS - 6, ROWS - 7), (COLS - 5, ROWS - 7)],
                  'left', strategy_green),
            Snake('蓝', [(COLS // 2, 3), (COLS // 2, 2), (COLS // 2, 1)], 'down', strategy_blue),
        ]
        self.foods = []
        self.poison_foods = []                                    #  新增：缩短食物列表
        self.messages = []
        self.over = False
        self.winner = None

        for _ in range(FOOD_NUM):
            self.spawn_food()
        for _ in range(POISON_NUM):                               #  新增：初始生成缩短食物
            self.spawn_poison_food()


 # ---------- 食物生成 ----------
    def _free_cells(self):                                        #  新增：统一空格计算
        occupied = set()
        for s in self.snakes:
            if s.alive:
                occupied.update(s.body)
        occupied.update(self.foods)
        occupied.update(self.poison_foods)                        #  新增：缩短食物也避开
        return [(x, y) for x in range(COLS) for y in range(ROWS)
                if (x, y) not in occupied]

    def spawn_food(self):
        free = self._free_cells()                                 #  修改：用 _free_cells
        if not free:
            return False
        self.foods.append(random.choice(free))
        return True

    def spawn_poison_food(self):                                  #  新增：生成缩短食物
        free = self._free_cells()
        if not free:
            return False
        self.poison_foods.append(random.choice(free))
        return True

    def step(self):
        alive = [s for s in self.snakes if s.alive]
        if len(alive) <= 1:
            return

        new_dirs = {}
        for s in alive:
            d = s.strategy(self, s)
            new_dirs[s] = d if d in DIRS else s.direction

        heads = {}
        for s in alive:
            dx, dy = DIRS[new_dirs[s]]
            heads[s] = (s.body[0][0] + dx, s.body[0][1] + dy)

        deaths = {}

        for s in alive:
            h = heads[s]
            if not in_bounds(h):
                deaths[s] = "撞到墙壁"
                continue
            
            ate_normal = h in self.foods                        #  新增
            ate_poison = h in self.poison_foods                 #  新增

            # ★ 修改：精确判定自撞（区分普通食物 / 缩短食物 / 普通移动）
            if ate_normal:
                own_body = s.body                               # 尾巴不缩
            elif ate_poison:
                own_body = s.body[:-2] if len(s.body) > 2 else s.body[:-1]  # 尾巴缩两格
            else:
                own_body = s.body[:-1]                          # 普通移动缩一格

            if h in own_body:
                deaths[s] = "撞到自己身体"
                continue

            for o in alive:
                if o is s:
                    continue
                if h in o.body[:-1]:
                    deaths[s] = f"撞到{o.name}色蛇的身体"
                    break

        for i in range(len(alive)):
            for j in range(i + 1, len(alive)):
                a, b = alive[i], alive[j]
                if heads[a] == heads[b]:
                    deaths.setdefault(a, f"与{b.name}色蛇迎面相撞")
                    deaths.setdefault(b, f"与{a.name}色蛇迎面相撞")

        for s in alive:
            if s in deaths:
                continue
            s.direction = new_dirs[s]
            h = heads[s]
            
            ate_normal = h in self.foods                        # 新增
            ate_poison = h in self.poison_foods                 # 新增

            if ate_normal:
                # 普通食物：生长（插头，不删尾）
                self.foods.remove(h)
                s.body.insert(0, h)

            elif ate_poison:                                    # 新增：缩短食物分支
                # 缩短食物：插头后删两格尾巴（净缩短 1）
                self.poison_foods.remove(h)
                s.body.insert(0, h)
                if len(s.body) < 4:      # 缩短后长度 < 2 → 死亡
                    s.alive = False
                    s.death_reason = "吃下缩短食物后身体长度不足"
                    self.messages.append(
                        (f"{s.name}色蛇出局：吃下缩短食物后身体长度不足", s.color))
                    continue
                s.body.pop()
                s.body.pop()

            else:
                # 普通移动
                s.body.insert(0, h)
                s.body.pop()


        for s in alive:
            if s in deaths:
                s.alive = False
                s.death_reason = deaths[s]
                self.messages.append((f"{s.name}色蛇出局：{deaths[s]}", s.color))

        while len(self.foods) < FOOD_NUM:
            if not self.spawn_food():
                break
        while len(self.poison_foods) < POISON_NUM:              # ★ 新增：补充缩短食物
            if not self.spawn_poison_food():
                break
       
        remaining = [s for s in self.snakes if s.alive]
        if len(remaining) == 1:
            self.over = True
            self.winner = remaining[0]
            self.messages.append((f"{self.winner.name}色蛇获胜！", self.winner.color))
        elif len(remaining) == 0:
            self.over = True
            self.messages.append(("所有蛇同时出局，平局！", (255, 220, 120)))

    def draw(self, screen, font):
        board_h = ROWS * CELL
        screen.fill(BG_COLOR)

        for x in range(0, WIDTH + 1, CELL):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, board_h))
        for y in range(0, board_h + 1, CELL):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

        for s in self.snakes:
            if not s.alive:
                continue
            for i, p in enumerate(s.body):
                rect = pygame.Rect(p[0] * CELL + 1, p[1] * CELL + 1, CELL - 2, CELL - 2)
                if i == 0:
                    color = tuple(min(255, c + 70) for c in s.color)
                else:
                    color = s.color
                pygame.draw.rect(screen, color, rect, border_radius=5)

        for f in self.foods:
            cx = f[0] * CELL + CELL // 2
            cy = f[1] * CELL + CELL // 2
            pygame.draw.circle(screen, FOOD_COLOR, (cx, cy), CELL // 2 - 2)
            pygame.draw.circle(screen, (255, 250, 210), (cx - 2, cy - 2), 2)
            # 缩短食物：品红圆点 + 白色 ×                          # 新增：绘制缩短食物
        for f in self.poison_foods:
            cx = f[0] * CELL + CELL // 2
            cy = f[1] * CELL + CELL // 2
            r = CELL // 2 - 2
            pygame.draw.circle(screen, POISON_COLOR, (cx, cy), r)
            d = 4
            pygame.draw.line(screen, (255, 255, 255),
                             (cx - d, cy - d), (cx + d, cy + d), 2)
            pygame.draw.line(screen, (255, 255, 255),
                             (cx - d, cy + d), (cx + d, cy - d), 2)

        pygame.draw.rect(screen, PANEL_BG, (0, board_h, WIDTH, PANEL_H))
        pygame.draw.line(screen, (90, 92, 120), (0, board_h), (WIDTH, board_h), 2)

        y = board_h + 10
        for text, color in self.messages[-3:]:
            surf = font.render(text, True, color)
            screen.blit(surf, (14, y))
            y += 27

        if not self.messages:
            surf = font.render("三条蛇正在自由竞技……", True, (150, 150, 170))
            screen.blit(surf, (14, board_h + 10))


# ==================== 主循环 ====================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("三蛇争霸 —— 三种策略的贪吃蛇对决")
    clock = pygame.time.Clock()

    # ---- 直接按文件路径加载中文字体，绕过 pygame 在 Windows 上的 SysFont bug ----
    def make_font(size=19):
        candidates = [
            r"C:\Windows\Fonts\msyh.ttc",      # 微软雅黑
            r"C:\Windows\Fonts\msyhbd.ttc",
            r"C:\Windows\Fonts\msyhl.ttc",
            r"C:\Windows\Fonts\simhei.ttf",    # 黑体
            r"C:\Windows\Fonts\simsun.ttc",    # 宋体
            r"C:\Windows\Fonts\simkai.ttf",    # 楷体
            r"C:\Windows\Fonts\simfang.ttf",   # 仿宋
            r"C:\Windows\Fonts\Deng.ttf",      # 等线
            r"C:\Windows\Fonts\msjh.ttc",      # 微软正黑体
            "/System/Library/Fonts/PingFang.ttc",           # macOS
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    return pygame.font.Font(path, size)
                except Exception:
                    continue
        return pygame.font.Font(None, size)

    font = make_font(19)

    game = Game()
    last_step = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game = Game()
                    last_step = pygame.time.get_ticks()

        now = pygame.time.get_ticks()
        if not game.over and now - last_step >= STEP_MS:
            last_step = now
            game.step()

        game.draw(screen, font)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

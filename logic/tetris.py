import random
from enum import IntEnum

from settings import Settings


class Action(IntEnum):
    NOOP = 0; LEFT = 1; RIGHT = 2; ROTATE_R = 3; ROTATE_L = 4; SOFT_DROP = 5; HARD_DROP = 6; HOLD=7


LINE_SCORES   = (0, 100, 300, 500, 800)
PERFECT_CLEAR = (0, 800, 1200, 1800, 2000)
PERFECT_CLEAR_B2B_TETRIS = 3200
LOCK_DELAY = 0.5
MAX_RESETS = 15

class TetrisGame:

    HIDDEN=4

    def __init__(self, game, size=None, height=None, width=None, seed=None):
        self.Game=game
        self.h=height if height else (size[1] if size else 10)
        self.w=width if width else (size[0] if size else 10)
        self.rng=random.Random(seed)
        self.reset()

    def reset(self):
        self.rows=self.h+self.HIDDEN
        self.board=[[0]*self.w for i in range(self.rows)]
        self.hold=None
        self.combo = -1
        self.back_to_back = False
        self.bag=[]
        self.score=self.lines=0
        self.game_over=False
        self.next_piece=self.get_piece()
        self.spawn()

    def get_piece(self):
        if len(self.bag)<=3:
            tmp=list(self.Game.settings.get("PIECES"))
            self.rng.shuffle(tmp)
            self.bag = tmp + self.bag
        return self.bag.pop()

    def spawn(self):
        self.current_piece = self.next_piece
        self.next_piece = self.get_piece()
        if not self.place_current():
            self.game_over = True
        self.can_hold = True

    def collides(self, cells, x,y):
        for cX, cY in cells:
            pX=x+cX
            pY=y+cY
            if pX<0 or pX>=self.w or pY<0 or pY>=self.rows:
                return True
            elif pY>=0 and self.board[pY][pX]:
                return True
        return False

    def move(self, dx):
        if not (self.collides(self.cells, self.x+dx, self.y)):
            self.x+=dx
            self.after_adjust()

    def reset_lock(self):
        self.lock_timer = 0.0
        self.lock_resets = 0
        self.lowest_y = self.y

    def grounded(self):
        return self.collides(self.cells, self.x, self.y + 1)

    def rotate(self, direction):
        if direction==1:
            newRotation=self.Game.settings.get("ROTATIONS")[(self.Game.settings.get("ROTATIONS").index(self.rotation)+1)%len(self.Game.settings.get("ROTATIONS"))]
            rotated=[(-cy,cx) for cx,cy in self.cells]
        elif direction==-1:
            newRotation=self.Game.settings.get("ROTATIONS")[(self.Game.settings.get("ROTATIONS").index(self.rotation)-1)%len(self.Game.settings.get("ROTATIONS"))]
            rotated = [(cy, -cx) for cx, cy in self.cells]
        else:
            newRotation=self.rotation
            rotated=self.cells
        shifts=[]
        for i in range(len(self.Game.settings.get("SRS_OFFSETS/"+self.current_piece+"/"+self.rotation))):
            offsets1=self.Game.settings.get("SRS_OFFSETS/"+self.current_piece+"/"+self.rotation)[i]
            offsets2=self.Game.settings.get("SRS_OFFSETS/"+self.current_piece+"/"+newRotation)[i]
            x1=offsets1["x"]
            y1=offsets1["y"]
            x2=offsets2["x"]
            y2=offsets2["y"]
            shifts.append((x1-x2,y1-y2))
        for shift in shifts:
            if not self.collides(rotated, self.x + shift[0], self.y+shift[1]):
                self.cells= rotated
                self.x = self.x + shift[0]
                self.y = self.y +shift[1]
                self.rotation=newRotation
                self.after_adjust()
                return

    def update_lock(self, dt):
        if self.game_over:
            return 0
        if self.grounded():
            self.lock_timer += dt
            if self.lock_timer >= LOCK_DELAY:
                return self.lock_piece()
        else:
            self.lock_timer = 0.0
        return 0

    def lock_piece(self):
        for cX, cY in self.cells:
            self.board[self.y + cY][self.x + cX] = self.Game.settings.get("PIECES").index(self.current_piece) + 1
        if all(self.y + cY < self.HIDDEN for cX, cY in self.cells):
            self.game_over = True
            return 0
        remaining = [r for r in self.board if not all(r)]
        cleared = self.rows - len(remaining)
        self.board = [[0] * self.w for _ in range(cleared)] + remaining
        self.lines += cleared

        self.spawn()
        return cleared

    def place_current(self):
        self.cells = self.Game.settings.get("BASE/"+self.current_piece)
        self.cells = [(item["x"],item["y"]) for item in self.cells ]
        self.rotation = self.Game.settings.get("ROTATIONS")[0]
        self.x = self.w // 2 - 1
        self.y = self.HIDDEN - 1
        if self.collides(self.cells, self.x, self.y):
            return False
        if not self.collides(self.cells, self.x, self.y + 1):
            self.y += 1
        self.reset_lock()
        return True

    def hold_piece(self):
        if self.can_hold:
            if self.hold is not None:
                self.hold, self.current_piece = self.current_piece, self.hold
                if not self.place_current():
                    self.game_over = True
            else:
                self.hold=self.current_piece
                self.spawn()
        self.can_hold=False

    def after_fall(self):
        if self.y > self.lowest_y:
            self.lowest_y = self.y
            self.lock_resets = 0
        self.lock_timer = 0.0

    def after_adjust(self):
        if self.y > self.lowest_y:
            self.lowest_y = self.y
            self.lock_resets = 0
        if self.grounded() and self.lock_resets < MAX_RESETS:
            self.lock_timer = 0.0
            self.lock_resets += 1

    def gravity(self):
        if self.game_over:
            return 0
        if not self.grounded():
            self.y += 1
            self.after_fall()
        return 0

    def soft_drop(self):
        if not self.grounded():
            self.y += 1
            self.score += 1
            self.after_fall()

    def act(self, action):
        if self.game_over:
            return 0
        if action=="LEFT":
            self.move(-1)
        elif action=="RIGHT":
            self.move(1)
        elif action=="ROTATE_R":
            self.rotate(1)
        elif action=="ROTATE_L":
            self.rotate(-1)
        elif action=="SOFT_DROP":
            self.soft_drop()
        elif action=="HOLD":
            self.hold_piece()
        elif action=="HARD_DROP":
            while  not self.collides(self.cells, self.x, self.y+1):
                self.y+=1
                self.score += 2
            return self.lock_piece()
        return 0

    def get_game_info(self):
        return{
            "board":self.get_table(),
            "bag":self.bag,
            "hold":self.hold,
        }

    def get_table(self):
        grid = [row[:] for row in self.board]
        if not self.game_over:
            cX=self.x
            cY=self.y
            cPiece=self.current_piece
            cCells=self.cells
            while not self.collides(cCells, cX, cY+1):
                cY+=1
            for cellX,cellY in cCells:
                grid[cY+cellY][cX+cellX]=len(self.Game.settings.get("PIECES"))+1
            for cx, cy in self.cells:
                grid[self.y + cy][self.x + cx] = self.Game.settings.get("PIECES").index(self.current_piece) + 1
        return grid[self.HIDDEN:]

    def get_held(self):
        return self.hold

    def get_bag(self):
        return self.bag

    def get_next(self):
        return [*self.bag,self.next_piece]

    def get_level(self):
        return self.lines//10+1

    def get_drop_time(self):
        return (0.8 - (self.get_level() - 1) * 0.007) ** (self.get_level() - 1)

    def add_score(self, cleared):
        level = self.get_level()
        if cleared == 0:
            self.combo = -1
            return
        self.combo += 1
        difficult = (cleared == 4)
        perfect = not any(any(row) for row in self.board)

        if perfect:
            points = PERFECT_CLEAR[cleared]
            if difficult and self.back_to_back:
                points = PERFECT_CLEAR_B2B_TETRIS
        else:
            points = LINE_SCORES[cleared]
            if difficult and self.back_to_back:
                points = points * 3 // 2

        points = points * level + 50 * self.combo * level
        self.back_to_back = difficult
        self.score += points


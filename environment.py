from logic.tetris import *
import numpy as np
from colorama import Fore

WEIGHTS = dict(game_over=-10.0, piece=1.0, height=0.0, holes=-1.0, bump=-0.1, missed=-1.0, max_height=0.0)
LINE_REWARD = {0: 0.0, 1: 5.0, 2: 15.0, 3: 30.0, 4: 50.0}
N_PREVIEW = 3
PIECES = ["I", "O", "T", "S", "Z", "J", "L"]
HOLD_PIECES = [None] + PIECES
HIDDEN_ROWS = 4
ROT_KEYS = [[], ["ROTATE_R"], ["ROTATE_180"], ["ROTATE_L"]]

def print_board(board):
    colors = {
        0: Fore.BLACK, 1: Fore.CYAN, 2: Fore.YELLOW, 3: Fore.MAGENTA,
        4: Fore.GREEN, 5: Fore.RED, 6: Fore.BLUE, 7: Fore.WHITE,
    }
    for line in board:
        for item in line:
            print(colors[item] + str(item), end="")
        print()
    print(Fore.WHITE)



def one_hot(value, options):
    result = np.zeros(len(options), dtype=np.float32)
    if value in options:
        result[options.index(value)] = 1.0
    return result


def column_heights(board):
    b = np.asarray(board)[HIDDEN_ROWS:] > 0
    h = b.shape[0]
    return np.where(b.any(axis=0), h - b.argmax(axis=0), 0)


def encode_state(tetris):
    b = np.asarray(tetris.board)[HIDDEN_ROWS:] > 0
    rows = b.shape[0]
    heights = column_heights(tetris.board).astype(np.float32) / rows

    queue = tetris.get_next()[:3]
    queue_enc = [one_hot(p, PIECES) for p in queue]

    return np.concatenate([
        b.astype(np.float32).flatten(),
        heights,
        one_hot(tetris.current_piece, PIECES),
        *queue_enc,
        one_hot(tetris.hold, HOLD_PIECES),
    ])

def board_features(board):
    b = np.asarray(board)[HIDDEN_ROWS:] > 0
    h, w = b.shape

    heights = column_heights(board)

    holes = 0
    for c in range(w):
        col = b[:, c]
        if col.any():
            top = col.argmax()
            holes += int((~col[top:]).sum())

    bumpiness = int(np.abs(np.diff(heights)).sum())

    return int(heights.sum()), holes, bumpiness, int(heights.max())

def shaped_reward(tetris, prev, curr, cleared):
    rows = tetris.h
    over = lambda m: max(0, m - rows // 2)
    r = LINE_REWARD.get(cleared, 0.0)
    r += WEIGHTS["height"] * (curr[0] - prev[0])
    r += WEIGHTS["holes"] * (curr[1] - prev[1])
    r += WEIGHTS["bump"] * (curr[2] - prev[2])
    r += WEIGHTS["max_height"] * (over(curr[3]) - over(prev[3]))
    return r

def get_state(tetris):
    return (
        tetris.board,
        tetris.current_piece,
        tetris.x,
        tetris.y,
        tetris.rotation,
        tetris.hold
    )

class PlaceChoiceEnv:
    def __init__(self, game, size=None, height=None, width=None, seed=None, verbose=False):
        self.tetris = TetrisGame(game, size=size, height=height, width=width, seed=seed)
        self.tetris.reset()
        self.lines = self.tetris.lines
        self.steps = 0
        self.missed = 0
        self.verbose = verbose

    @property
    def n_actions(self):
        return 2 * 4 * self.tetris.w

    def execute(self, t, action):
        w = t.w
        use_hold, rest = divmod(int(action), 4 * w)
        rotation, target_x = divmod(rest, w)

        if use_hold:
            if not t.can_hold:
                return False
            t.act("HOLD")
            if t.game_over:
                return False

        for key in ROT_KEYS[rotation]:
            t.act(key)
        rots =["0","R","2","L"]
        ok = rots.index(t.rotation) == rotation

        for _ in range(w):
            x = t.x
            if x == target_x:
                break
            t.act("LEFT" if x > target_x else "RIGHT")
            if t.x == x:
                break
        ok = ok and t.x == target_x

        t.act("HARD_DROP")
        return ok

    def legal_actions(self):
        t0 = self.tetris
        w = t0.w
        mask = np.zeros(self.n_actions, dtype=bool)
        rots = ROT_KEYS
        seen = set()

        for use_hold in (0, 1):
            if use_hold and not t0.can_hold:
                continue
            base = t0.clone()
            if use_hold:
                base.act("HOLD")
                if base.game_over:
                    continue

            for rot in range(4):
                sim = base.clone()
                for key in ROT_KEYS[rot]:
                    sim.act(key)
                if rots.index(sim.rotation) != rot:  # rotation failed
                    continue

                lo = sim.x
                while not sim.collides(sim.cells, lo - 1, sim.y):
                    lo -= 1
                hi = sim.x
                while not sim.collides(sim.cells, hi + 1, sim.y):
                    hi += 1

                for x in range(max(lo, 0), min(hi, w - 1) + 1):
                    y = sim.y
                    while not sim.collides(sim.cells, x, y + 1):
                        y += 1
                    key = (use_hold, frozenset((x + cx, y + cy) for cx, cy in sim.cells))
                    if key in seen:  # same landing, e.g. O-piece rotations
                        continue
                    seen.add(key)
                    mask[use_hold * 4 * w + rot * w + x] = True

        if not mask.any():
            mask[:] = True
        return mask

    def reset(self):
        self.tetris.reset()
        self.lines = self.tetris.lines
        self.steps = 0
        self.missed = 0
        return encode_state(self.tetris)

    def act(self, action):
        t = self.tetris
        prev = board_features(t.board)
        ok = self.execute(t, action)
        if not ok:
            self.missed += 1

        self.steps += 1
        cleared = t.lines - self.lines
        self.lines = t.lines

        reward = shaped_reward(self.tetris, prev, board_features(t.board), cleared)
        reward += WEIGHTS["piece"]
        done = t.game_over
        if done:
            reward += WEIGHTS["game_over"]
            if self.verbose:
                print_board(self.tetris.board)
        return encode_state(t), reward, done



class EveryChoiceEnv:
    def __init__(self, game, size=None, height=None, width=None, seed=None, verbose=False):
        self.tetris = TetrisGame(game, size=size, height=height, width=width, seed=seed)
        self.tetris.reset()
        self.lines = self.tetris.lines
        self.steps = 0
        self.verbose = verbose
        self.actions=["LEFT", "RIGHT", "SOFT DROP", "HARD DROP", "ROTATE_R", "ROTATE_L", "ROTATE_180", "HARD_DROP", "HOLD", "NONE"]

    @property
    def n_actions(self):
        return len(self.actions)

    def act(self, action):
        pass
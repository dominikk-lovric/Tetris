from logic.tetris import *
import numpy as np
from colorama import Fore

WEIGHTS = dict(
    game_over=-40.0,
    piece=0.3,
    height=-0.1,
    holes=-1,
    bump=-0.2,
    missed=-1.0,
)
LINE_REWARD = {0: 0.0, 1: 5.0, 2: 15.0, 3: 30.0, 4: 50.0}

PIECES = ["I", "O", "T", "S", "Z", "J", "L"]
HOLD_PIECES = [None] + PIECES
HIDDEN_ROWS = 4
ROT_KEYS = [[], ["ROTATE_R"], ["ROTATE_180"], ["ROTATE_L"]]


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

    return np.concatenate([
        b.astype(np.float32).flatten(),
        heights,
        one_hot(tetris.current_piece, PIECES),
        one_hot(tetris.next_piece, PIECES),
        one_hot(tetris.hold, HOLD_PIECES),
    ])


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
        return 4 * self.tetris.w

    def reset(self):
        self.tetris.reset()
        self.lines = self.tetris.lines
        self.steps = 0
        self.missed = 0
        return encode_state(self.tetris)

    def get_state(self):
        return (
            self.tetris.board,
            self.tetris.current_piece,
            self.tetris.x,
            self.tetris.y,
            self.tetris.rotation,
            self.tetris.hold
        )

    def act(self, action):
        t = self.tetris
        rotation, target_x = divmod(int(action), t.w)

        prev_features = self.board_features(t.board)

        for key in ROT_KEYS[rotation]:
            t.act(key)

        for _ in range(t.w):
            x = t.x
            if x == target_x:
                break
            t.act("LEFT" if x > target_x else "RIGHT")
            if t.x == x:
                break

        missed = t.x != target_x

        locked = t.act("HARD_DROP")
        while not locked and not t.game_over:
            locked = t.gravity()

        self.steps += 1
        cleared = t.lines - self.lines

        reward = self.shaped_reward(prev_features, self.board_features(t.board), cleared)
        reward += WEIGHTS["piece"]

        if missed:
            reward += WEIGHTS["missed"]
            self.missed += 1

        done = t.game_over
        if done:
            reward += WEIGHTS["game_over"]
            if self.verbose:
                self.print_board()

        self.lines = t.lines
        return encode_state(t), reward, done

    def board_features(self, board):
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

    def shaped_reward(self, prev, curr, cleared):
        r = LINE_REWARD.get(cleared, 0.0)
        r += WEIGHTS["height"] * (curr[0] - prev[0])
        r += WEIGHTS["holes"] * (curr[1] - prev[1])
        r += WEIGHTS["bump"] * (curr[2] - prev[2])
        return r

    def print_board(self):
        colors = {
            0: Fore.BLACK, 1: Fore.CYAN, 2: Fore.YELLOW, 3: Fore.MAGENTA,
            4: Fore.GREEN, 5: Fore.RED, 6: Fore.BLUE, 7: Fore.WHITE,
        }
        for line in self.tetris.board:
            for item in line:
                print(colors[item] + str(item), end="")
            print()
        print(Fore.WHITE)


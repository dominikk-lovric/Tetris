import json
import os
import sys
import shutil
from pathlib import Path

DEFAULT={
    "KEYBINDS": {
        "KEYMAP": {
            "ROTATE_R": [
                "right"
            ],
            "ROTATE_L": [
                "left"
            ],
            "HARD_DROP": [
                "space"
            ],
            "HOLD": [
                "left shift"
            ]
        },
        "REPEAT_KEYS": {
            "SOFT_DROP": {
                "delay": 0,
                "repeat": 0.04,
                "binds": [
                    "s"
                ]
            },
            "LEFT": {
                "delay": 0.17,
                "repeat": 0.05,
                "binds": [
                    "a"
                ]
            },
            "RIGHT": {
                "delay": 0.17,
                "repeat": 0.05,
                "binds": [
                    "d"
                ]
            }
        }
    },
    "MENU_SIZE": {
        "x": 1200,
        "y": 800
    },
    "COLORS": {
        "BG": {
            "R": 0,
            "G": 0,
            "B": 0
        },
        "FG": {
            "R": 200,
            "G": 200,
            "B": 200
        },
        "HIGHLIGHT": {
            "R": 255,
            "G": 255,
            "B": 255
        },
        "DIM": {
            "R": 110,
            "G": 110,
            "B": 110
        },
        "PIECE_COLORS": {
            "I": {
                "R": 40,
                "G": 230,
                "B": 210
            },
            "O": {
                "R": 230,
                "G": 220,
                "B": 40
            },
            "T": {
                "R": 200,
                "G": 40,
                "B": 230
            },
            "S": {
                "R": 100,
                "G": 230,
                "B": 40
            },
            "Z": {
                "R": 230,
                "G": 40,
                "B": 40
            },
            "J": {
                "R": 12,
                "G": 82,
                "B": 161
            },
            "L": {
                "R": 230,
                "G": 155,
                "B": 40
            },
            "PREVIEW": {
                "R": 68,
                "G": 68,
                "B": 68
            }
        }
    },
    "PIECES": [
        "I",
        "O",
        "T",
        "S",
        "Z",
        "J",
        "L"
    ],
    "BASE": {
        "I": [
            {
                "x": -1,
                "y": 0
            },
            {
                "x": 0,
                "y": 0
            },
            {
                "x": 1,
                "y": 0
            },
            {
                "x": 2,
                "y": 0
            }
        ],
        "O": [
            {
                "x": 0,
                "y": 0
            },
            {
                "x": 1,
                "y": 0
            },
            {
                "x": 0,
                "y": -1
            },
            {
                "x": 1,
                "y": -1
            }
        ],
        "T": [
            {
                "x": -1,
                "y": 0
            },
            {
                "x": 0,
                "y": 0
            },
            {
                "x": 1,
                "y": 0
            },
            {
                "x": 0,
                "y": -1
            }
        ],
        "S": [
            {
                "x": 1,
                "y": -1
            },
            {
                "x": 0,
                "y": -1
            },
            {
                "x": 0,
                "y": 0
            },
            {
                "x": -1,
                "y": 0
            }
        ],
        "Z": [
            {
                "x": 1,
                "y": 0
            },
            {
                "x": 0,
                "y": 0
            },
            {
                "x": 0,
                "y": -1
            },
            {
                "x": -1,
                "y": -1
            }
        ],
        "J": [
            {
                "x": -1,
                "y": 0
            },
            {
                "x": 0,
                "y": 0
            },
            {
                "x": 1,
                "y": 0
            },
            {
                "x": -1,
                "y": -1
            }
        ],
        "L": [
            {
                "x": -1,
                "y": 0
            },
            {
                "x": 0,
                "y": 0
            },
            {
                "x": 1,
                "y": 0
            },
            {
                "x": 1,
                "y": -1
            }
        ]
    },
    "ROTATIONS": [
        "0",
        "R",
        "2",
        "L"
    ],
    "SRS_OFFSETS": {
        "I": {
            "0": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": -1,
                    "y": 0
                },
                {
                    "x": 2,
                    "y": 0
                },
                {
                    "x": -1,
                    "y": 0
                },
                {
                    "x": 2,
                    "y": 0
                }
            ],
            "R": [
                {
                    "x": -1,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": -1
                },
                {
                    "x": 0,
                    "y": 2
                }
            ],
            "2": [
                {
                    "x": -1,
                    "y": -1
                },
                {
                    "x": 1,
                    "y": -1
                },
                {
                    "x": -2,
                    "y": -1
                },
                {
                    "x": 1,
                    "y": 0
                },
                {
                    "x": -2,
                    "y": 0
                }
            ],
            "L": [
                {
                    "x": 0,
                    "y": -1
                },
                {
                    "x": 0,
                    "y": -1
                },
                {
                    "x": 0,
                    "y": -1
                },
                {
                    "x": 0,
                    "y": 1
                },
                {
                    "x": 0,
                    "y": -2
                }
            ]
        },
        "O": {
            "0": [
                {
                    "x": 0,
                    "y": 0
                }
            ],
            "R": [
                {
                    "x": 0,
                    "y": 1
                }
            ],
            "2": [
                {
                    "x": -1,
                    "y": 1
                }
            ],
            "L": [
                {
                    "x": -1,
                    "y": 0
                }
            ]
        },
        "T": {
            "0": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                }
            ],
            "R": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 1,
                    "y": 0
                },
                {
                    "x": 1,
                    "y": 1
                },
                {
                    "x": 0,
                    "y": -2
                },
                {
                    "x": 1,
                    "y": -2
                }
            ],
            "2": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                }
            ],
            "L": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": -1,
                    "y": 0
                },
                {
                    "x": -1,
                    "y": 1
                },
                {
                    "x": 0,
                    "y": -2
                },
                {
                    "x": -1,
                    "y": -2
                }
            ]
        },
        "S": {
            "0": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                }
            ],
            "R": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 1,
                    "y": 0
                },
                {
                    "x": 1,
                    "y": 1
                },
                {
                    "x": 0,
                    "y": -2
                },
                {
                    "x": 1,
                    "y": -2
                }
            ],
            "2": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                }
            ],
            "L": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": -1,
                    "y": 0
                },
                {
                    "x": -1,
                    "y": 1
                },
                {
                    "x": 0,
                    "y": -2
                },
                {
                    "x": -1,
                    "y": -2
                }
            ]
        },
        "Z": {
            "0": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                }
            ],
            "R": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 1,
                    "y": 0
                },
                {
                    "x": 1,
                    "y": 1
                },
                {
                    "x": 0,
                    "y": -2
                },
                {
                    "x": 1,
                    "y": -2
                }
            ],
            "2": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                }
            ],
            "L": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": -1,
                    "y": 0
                },
                {
                    "x": -1,
                    "y": 1
                },
                {
                    "x": 0,
                    "y": -2
                },
                {
                    "x": -1,
                    "y": -2
                }
            ]
        },
        "J": {
            "0": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                }
            ],
            "R": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 1,
                    "y": 0
                },
                {
                    "x": 1,
                    "y": 1
                },
                {
                    "x": 0,
                    "y": -2
                },
                {
                    "x": 1,
                    "y": -2
                }
            ],
            "2": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                }
            ],
            "L": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": -1,
                    "y": 0
                },
                {
                    "x": -1,
                    "y": 1
                },
                {
                    "x": 0,
                    "y": -2
                },
                {
                    "x": -1,
                    "y": -2
                }
            ]
        },
        "L": {
            "0": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                }
            ],
            "R": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 1,
                    "y": 0
                },
                {
                    "x": 1,
                    "y": 1
                },
                {
                    "x": 0,
                    "y": -2
                },
                {
                    "x": 1,
                    "y": -2
                }
            ],
            "2": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": 0,
                    "y": 0
                }
            ],
            "L": [
                {
                    "x": 0,
                    "y": 0
                },
                {
                    "x": -1,
                    "y": 0
                },
                {
                    "x": -1,
                    "y": 1
                },
                {
                    "x": 0,
                    "y": -2
                },
                {
                    "x": -1,
                    "y": -2
                }
            ]
        }
    },
    "SIZES": {
        "SMALL": {
            "x": 5,
            "y": 20
        },
        "NORMAL": {
            "x": 10,
            "y": 20
        },
        "LARGE": {
            "x": 15,
            "y": 20
        }
    },
    "HIGHSCORE": {
        "SMALL": 0,
        "NORMAL": 0,
        "LARGE": 0
    },
    "UNIT": 16
}

def get_resource_path(filename):
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / filename


def get_user_settings_path():
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
        folder = base / "MyGame"
    elif sys.platform == "darwin":
        folder = Path.home() / "Library" / "Application Support" / "MyGame"
    else:
        folder = Path(
            os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
        ) / "mygame"

    folder.mkdir(parents=True, exist_ok=True)
    return folder / "settings.json"


class Settings:
    def __init__(self):
        self.path = "./settings.json"
        try:
            with open(self.path,"r", encoding="utf-8") as json_file:
                self.data=json.load(json_file)
        except FileNotFoundError:
            with open("./settings.json","w", encoding="utf-8") as json_file:
                json.dump(DEFAULT,json_file)
                self.data=DEFAULT

    def get(self, path):
        cur = self.data
        for key in path.split("/"):
            if  isinstance(cur, list) and key.isdigit():
                if len(cur)-1<int(key):
                    return None
                cur=cur[int(key)]
            elif not isinstance(cur, dict) or key not in cur:
                return None
            else:
                cur = cur[key]
        return cur

    def set(self, path, value):
        keys = path.split("/")
        cur = self.data
        for key in keys[:-1]:
            if isinstance(cur, list):
                cur = cur[int(key)]
            else:
                if not isinstance(cur.get(key), (dict, list)):
                    cur[key] = {}
                cur = cur[key]

        last = keys[-1]
        if isinstance(cur, list):
            i = int(last)
            if i == len(cur):
                cur.append(value)
            else:
                cur[i] = value
        else:
            cur[last] = value
        self.save()

    def save(self):
        with open("settings.json","w", encoding="utf-8") as json_file:
            json.dump(self.data, json_file, ensure_ascii=False, indent=4)

    def get_touple(self,path):
        items=self.get(path)
        if items is None:
            return ()
        if isinstance(items, dict):
            return tuple(items.values())
        if isinstance(items, (list, tuple)):
            return tuple(items)
        return (items,)

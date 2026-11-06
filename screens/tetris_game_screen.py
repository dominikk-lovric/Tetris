import pygame
from elements.column import Column
from elements.padding import Padding
from elements.row import Row
from elements.tetris_field import TetrisField
from elements.text import Text
from logic.tetris import *
from screen import Screen
from screens.game_over_screen import GameOverScreen
from screens.pause_screen import PauseScreen

class TetrisGameScreen(Screen):
    GRAVITY_INTERVAL=0.5
    def __init__(self, game, width=None, height=None, size=None):
        self.Game=game
        sizeX = width if width is not None else size[0] if size is not None else 10
        sizeY = (height if height is not None else size[1] if size is not None else 20)
        self.tetris=TetrisGame(self.Game, width=sizeX,height=sizeY)
        self.size = (sizeX, sizeY)
        self.bg=self.Game.settings.get_touple("COLORS/BG")
        self.acc = 0.0
        self.held = {}
        self.held_block=""
        self.held_box=box=self.get_box(5,5,self.Game.settings.get_touple("COLORS/HIGHLIGHT"), 2)
        self.table=TetrisField(game, sizeX, sizeY, cell="[]", wall="|", floor="__", size=int(self.Game.settings.get("UNIT")*1.5))
        self.keymap, self.repeat = self.get_keybinds(self.Game.settings)

    def get_keybinds(self, settings):
        keymap_setting=settings.get("KEYBINDS/KEYMAP")
        keymap_setting_keys=list(keymap_setting.keys())
        keymap={}
        for key in keymap_setting_keys:
            keymap[key]=self.get_key(keymap_setting[key])
        repeated_setting=settings.get("KEYBINDS/REPEAT_KEYS")
        repeated_setting_keys=list(repeated_setting.keys())
        repeated={}
        for key in repeated_setting_keys:
            repeated[key]=(repeated_setting[key]["delay"], repeated_setting[key]["repeat"], self.get_key(repeated_setting[key]["binds"]))
        return keymap, repeated

    def get_key(self, list):
        keys=[]
        for key in list:
            try:
               keys.append(pygame.key.key_code(key))
            except:
                pass
        return keys

    def on_enter(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key:
            if event.key==pygame.K_ESCAPE:
                self.Game.push_screen(PauseScreen(self.Game))
            else:
                for key in self.keymap:
                    if(event.key in self.keymap[key]):
                        self.tetris.act(key)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        for action, (das, arr, keyList) in self.repeat.items():
            for key in keyList:
                if keys[key]:
                    if key not in self.held:
                        self.held[key] = [0.0, 0.0]
                        self.tetris.act(action)
                    else:
                        state = self.held[key]
                        state[0] += dt
                        if state[0] >= das:
                            state[1] += dt
                            while state[1] >= arr:
                                state[1] -= arr
                                self.tetris.act(action)
                else:
                    self.held.pop(key, None)
        interval=self.tetris.get_drop_time()
        self.acc += dt
        while self.acc >= interval:
            self.acc -= interval
            self.tetris.gravity()
        self.tetris.update_lock(dt)
        if(self.tetris.game_over):
            self.Game.pop_screen()
            self.Game.switch_screen(GameOverScreen(self.Game, self.size, self.tetris.score))

    def draw(self, surface):
        surface.fill(self.bg)
        self.table.set_grid(self.tetris.get_table())
        posX=surface.get_rect().center[0]-self.table.get_size()[0]/2
        posY=surface.get_rect().center[1]-self.table.get_size()[1]/2
        tetrisTable=Column([self.table], mainAxisAalignment="end")

        if self.held_block!=self.tetris.get_held():
            self.held_block=self.tetris.get_held()
        held=Column([Text("Held piece:",size = self.Game.settings.get("UNIT")),self.get_centered(self.get_piece(self.held_block), 6*self.Game.settings.get("UNIT"),6*self.Game.settings.get("UNIT"),self.Game.settings.get_touple("COLORS/HIGHLIGHT"),2), Text("Level: "+str(self.tetris.get_level()),size = self.Game.settings.get("UNIT")), Text("Score: "+str(self.tetris.score),size = self.Game.settings.get("UNIT")) ],spacing=self.Game.settings.get("UNIT")/2)
        held.draw(surface, ((posX-held.get_size()[0])/2,72))

        bag=[]
        for piece in self.tetris.get_next()[:3]:
            bag.append(self.get_centered(self.get_piece(piece), 6*self.Game.settings.get("UNIT"), 6*self.Game.settings.get("UNIT")))
        upcoming=Column([Text("Upcoming:",size = self.Game.settings.get("UNIT")),self.get_centered(Column(bag),6*24,20*24, self.Game.settings.get_touple("COLORS/HIGHLIGHT"), 2)], spacing=self.Game.settings.get("UNIT")/2)
        upcoming.draw(surface, ((posX+tetrisTable.get_size()[0]+surface.get_rect().width-upcoming.get_size()[0])/2,self.Game.settings.get("UNIT")*3))

        tetrisTable.draw(surface, (posX,-1*self.Game.settings.get("UNIT")))

    def get_box(self, x, y, border_color=None, border_size=0):
        return Padding(Column([Row([Text("  ",size = self.Game.settings.get("UNIT")) for j in range(x)]) for i in range (y)]), border_color=border_color, border=border_size)


    def get_centered(self, item, sizeX, sizeY, border_color=None, border_size=0):
        sizeX=sizeX
        sizeY=sizeY
        itemSize=item.get_size()
        paddingVertical=(sizeY-itemSize[1])/2
        paddingHorizontal=(sizeX-itemSize[0])/2
        return Padding(item, vertical=paddingVertical, horizontal=paddingHorizontal, border=border_size, border_color=border_color)

    def draw_bag(self, surface, pos, bag):
        posX=pos[0]
        posY=pos[1]
        box=self.get_box(5, 17, border_color=None, border_size=0)
        heldCol=Column([self.get_piece(piece) for piece in bag],spacing=self.Game.settings.get("UNIT"))
        box.draw(surface, (posX, posY))

    def get_piece(self, piece):
        if(piece is not None):
            cells=self.Game.settings.get("BASE")[piece]
            cells=[(item["x"], item["y"]) for item in cells]
            color=self.Game.settings.get_touple("COLORS/PIECE_COLORS/"+piece)
            min_x = min(x for x, y in cells)
            max_x = max(x for x, y in cells)
            min_y = min(y for x, y in cells)
            max_y = max(y for x, y in cells)
        else:
            cells=[]
            color=(0,0,0)
            min_x = 0
            max_x = 0
            min_y = 0
            max_y = 0
        Rows=[]
        for i in range(min_y,max_y+1,1):
            txt=""
            for j in range(min_x,max_x+1,1):
                if (j,i) in cells:
                    txt+="[]"
                else:
                    txt+="  "
            Rows.append(Text(txt,color=color,size = self.Game.settings.get("UNIT")))
        return Column(Rows)


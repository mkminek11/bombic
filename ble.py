import pyglet, easygui
from typing import Union

################################################################
#                                                              #
################################################################

def touching(x1:int, y1:int, width1:int, height1:int, x2:int, y2:int, width2:int, height2:int):
    if (x1 > x2 and x1 < x2 + width2) or (x2 > x1 and x2 < x1 + width1):
        if (y1 > y2 and y1 < y2 + height2) or (y2 > y1 and y2 < y1 + height1):
            return True
    return False

################################################################
#                                                              #
################################################################

class Block:
    def __init__(self, x:int, y:int, block_id:int, block_size:int, SPRITESHEET_HEIGHT, SPRITESHEET_WIDTH):
        self.bs = block_size
        self.image = pyglet.image.load("img/ble/top2.png")
        self.ss = pyglet.image.ImageGrid(self.image, SPRITESHEET_HEIGHT, SPRITESHEET_WIDTH, row_padding=1, column_padding=1)
        self.batch = pyglet.graphics.Batch()
        self.draw_x = 0
        self.draw_y = 0
        self.x = x
        self.y = y
        self.id = block_id
        if block_id >= 0:
            self.sprite = pyglet.sprite.Sprite(self.ss[block_id], z=y, batch=self.batch)
        else:
            self.sprite = pyglet.sprite.Sprite(self.ss[0], z=y, batch=self.batch)
        self.sprite.scale = block_size/self.sprite.width
        self.hid = False

    def draw(self):
        self.sprite.x = self.draw_x + self.bs*self.x
        self.sprite.y = self.draw_y + self.bs*self.y
        if not self.hid:
            self.batch.draw()
    
    def set_pos(self, x:Union[int, float], y:Union[int, float]):
        self.draw_x = x
        self.draw_y = y

    def change_id(self, new_id:int=0, h=True):
        if new_id >= 0 and new_id < len(self.ss):
            self.id = new_id
            self.sprite.image = self.ss[self.id]

################################################################
#                                                              #
################################################################

class Background:
    def __init__(self, x:int=0, y:int=0, width:int=0, height:int=0, color:tuple=(255, 255, 255), image:str=None, repeat_bg:bool=True, opacity:int=255):
        self.bg = pyglet.shapes.Rectangle(x, y, width, height, color)
        self.image = image
        self.repeat_bg = repeat_bg
        self.image = image
        self.opacity = opacity
        if self.image:
            self.img = pyglet.image.load(image)

    def draw(self):
        self.bg.draw()
        if self.image:
            n1 = -1
            n2 = -1
            for n1 in range(self.bg.width//self.img.width):
                for n2 in range(self.bg.height//self.img.height):
                    self.img.blit(self.bg.x+n1*self.img.width, self.bg.y+n2*self.img.height)
                n2 += 1
                a = pyglet.sprite.Sprite(self.img.get_region(0, 0, self.img.width, self.bg.height%self.img.height))
                a.x, a.y = self.bg.x+n1*self.img.width, self.bg.y+n2*self.img.height
                a.opacity = self.opacity
                a.draw()
            n1 += 1
            for n2 in range(self.bg.height//self.img.height):
                a = pyglet.sprite.Sprite(self.img.get_region(0, 0, self.bg.width%self.img.width, self.img.height))
                a.x, a.y = self.bg.x+n1*self.img.width, self.bg.y+n2*self.img.height
                a.opacity = self.opacity
                a.draw()
            n2 += 1
            a = pyglet.sprite.Sprite(self.img.get_region(0, 0, self.bg.width%self.img.width, self.bg.height%self.img.height))
            a.x, a.y = self.bg.x+n1*self.img.width, self.bg.y+n2*self.img.height
            a.opacity = self.opacity
            a.draw()

    def set_pos(self, x:int=0, y:int=0, width:int=0, height:int=0):
        self.bg.x = x
        self.bg.y = y
        self.bg.width = width
        self.bg.height = height

################################################################
#                                                              #
################################################################

class _SwitchOption:
    def __init__(self, image, x:int, y:int, scale:float):
        self.batch = pyglet.graphics.Batch()
        self.image = image
        self.sprite = pyglet.sprite.Sprite(self.image, x, y, batch=self.batch)
        self.sprite.scale = scale

    def change_pos(self, x, y):
        self.sprite.x = x
        self.sprite.y = y

    def draw(self):
        self.batch.draw()

################################################################
#                                                              #
################################################################

class Switch:
    def __init__(self, scale:int=1, x=0, y=0, images:list=[], chosen_images:list=[]):
        if len(images) < 2 or len(images) > 10:
            raise OverflowError("Too much options. Max count is 10.")

        self.options:list[_SwitchOption] = []
        self.images = images
        self.chosen_images = chosen_images

        self.chosen = 0

        for i in images:
            self.options.append(_SwitchOption(i, 0, 0, scale))
        self.set_pos(x, y)
        self._enable(self.chosen)
        
    def set_pos(self, x, y):
        for n, i in enumerate(self.options):
            i.change_pos(x+n*(i.sprite.width + 10), y)

    def draw(self):
        for i in self.options:
            i.draw()

    def change(self, option, enable=True):
        o = self.options.index(option)
        self.chosen = o
        if enable:
            self._enable(o)
        else:
            self._disable(o)

    def _enable(self, id):
        self.options[id].sprite.image = self.chosen_images[id]

    def _disable(self, id):
        self.options[id].sprite.image = self.images[id]

    def check(self, x, y):
        for i in self.options:
            if touching(x, y, 0, 0, i.sprite.x, i.sprite.y, i.sprite.width, i.sprite.height):
                for j in self.options:
                    self.change(j, False)
                self.change(i, True)

    def directions(self):
        height = self.options[0].sprite.height * self.options[0].sprite.scale
        width_1 = self.options[0].sprite.width * self.options[0].sprite.scale
        l = len(self.options)
        width = l * (width_1 + 10) - 10
        return width, height

################################################################
#                                                              #
################################################################

def get_block(x:int, y:int, height:int, pad_x:int, pad_y:int, block_size):
    dx = int((x - pad_x)//block_size)
    dy = int((height - y + pad_y)//block_size)
    return dx, dy


################################################################
#                       setting window                         #
################################################################

w = pyglet.window.Window(1000, 746, resizable=True)
w.set_minimum_size(600, 400)

keys = {}

################################################################
#                           constants                          #
################################################################

BLOCK_SIZE = 64
SIDEBAR_WIDTH = 320
ANIMATION_JUMP = 10
SPRITESHEET_WIDTH = 10
SPRITESHEET_HEIGHT= 4

################################################################
#                       field setting                          #
################################################################

blocks:list[Block] = []

################################################################
#                          switches                            #
################################################################

s1 = Switch(0.3, 0, 0,
    [
        pyglet.image.load("img/ble/icons.png").get_region(0,   256, 256, 128),  # build
        pyglet.image.load("img/ble/icons.png").get_region(0,   128, 256, 128),  # edit
        pyglet.image.load("img/ble/icons.png").get_region(0,   0,   256, 128)   # delete
    ],
    [
        pyglet.image.load("img/ble/icons.png").get_region(256, 256, 256, 128),
        pyglet.image.load("img/ble/icons.png").get_region(256, 128, 256, 128),
        pyglet.image.load("img/ble/icons.png").get_region(256, 0,   256, 128)
    ]
)

s2 = Switch(0.3, 0, 0,
    [
        pyglet.image.load("img/ble/icons.png").get_region(0,   384, 128, 128),
        pyglet.image.load("img/ble/icons.png").get_region(128, 384, 128, 128)
    ],
    [
        pyglet.image.load("img/ble/icons.png").get_region(256, 384, 128, 128),
        pyglet.image.load("img/ble/icons.png").get_region(384, 384, 128, 128)
    ]
)

################################################################
#                           settings                           #
################################################################

block_types = [Block(0, 0, SPRITESHEET_WIDTH * y + x, BLOCK_SIZE, SPRITESHEET_HEIGHT, SPRITESHEET_WIDTH) for x in range(SPRITESHEET_WIDTH) for y in range(SPRITESHEET_HEIGHT)]

active_block = block_types[0]
active_type = None

sidebar = pyglet.graphics.Batch()
sb_bg = Background(image="img\\ble\\pattern.png", opacity=100)

select_rect = pyglet.shapes.BorderedRectangle(0, 0, 0, 0, 2, (100, 150, 255), (50, 80, 255))
select_rect.opacity = 0

drag_start_x = 0
drag_start_y = 0

select_drag_x = 0
select_drag_y = 0

camera_x = 0
camera_y = 0

camera_stable_x = 0
camera_stable_y = 0

################################################################
#                        build functions                       #
################################################################

def click(x, y):
    match s1.chosen:
        case 0:
            build(x, y)
        case 1:
            edit(x, y)
        case 2:
            delete(x, y)

def try_place(ax, ay):
    sb = Block(ax, ay, active_block.id, BLOCK_SIZE, SPRITESHEET_HEIGHT, SPRITESHEET_WIDTH)
    for i in blocks:
        if ax == i[0] and ay == i[1]:
            blocks.remove(i)
    blocks.append((ax, ay, sb))

def build(x, y):
    global select_drag_x, select_drag_y
    sx = (x-camera_x-camera_stable_x)//BLOCK_SIZE
    sy = (y-camera_y-camera_stable_y)//BLOCK_SIZE
    try_place(sx, sy)

def edit(x, y):
    pass

def delete(x, y):
    occurrences = []
    for n, b in enumerate(blocks):
        if b[0] == (x-camera_x-camera_stable_x)//BLOCK_SIZE and b[1] == (y-camera_y-camera_stable_y)//BLOCK_SIZE:
            occurrences.append(n)
    try:
        del blocks[occurrences[-1]]
    except:
        pass

################################################################
#                      select build functoins                  #
################################################################

def select_build(x, y, sx, sy):
    sx = int((sx-camera_x-camera_stable_x)//BLOCK_SIZE)
    sy = int((sy-camera_y-camera_stable_y)//BLOCK_SIZE)
    tx = int((x -camera_x-camera_stable_x)//BLOCK_SIZE)
    ty = int((y -camera_y-camera_stable_y)//BLOCK_SIZE)
    for ax in range(abs(sx-tx)+1):
        for ay in range(abs(sy-ty)+1):
            try_place(min(sx,tx)+ax, min(sy,ty)+ay)

def select_delete(x, y, bx, by):
    sx = int((bx-camera_x-camera_stable_x)//BLOCK_SIZE)
    sy = int((by-camera_y-camera_stable_y)//BLOCK_SIZE)
    tx = int((x -camera_x-camera_stable_x)//BLOCK_SIZE)
    ty = int((y -camera_y-camera_stable_y)//BLOCK_SIZE)

    for ax in range(min(tx, sx), max(tx, sx)+1):
        for ay in range(min(ty, sy), max(ty, sy)+1):
            occurrences = []
            for n, b in enumerate(blocks):
                if b[0] == ax and b[1] == ay:
                    occurrences.append(n)
            try:
                del blocks[occurrences[-1]]
            except:
                pass

################################################################
#                         on draw                              #
################################################################

@w.event
def on_draw():
    w.clear()
    for x, y, bl in blocks:
        bl.set_pos(camera_stable_x+camera_x, camera_stable_y+camera_y)
        bl.draw()
    # ground_batch.draw()
    select_rect.draw()
    sidebar.draw()
    sb_bg.draw()
    if s1.chosen == 0:
        for n, i in enumerate(block_types):
            i.set_pos(w.width-SIDEBAR_WIDTH+10+(BLOCK_SIZE+10)*(n%4),     w.height-(n//4+1)*(BLOCK_SIZE+10)-s1.directions()[1]-s2.directions()[1]-100)
            i.draw()
    s1.set_pos(w.width - SIDEBAR_WIDTH + 10, w.height - 50)
    s1.draw()
    s2.set_pos(w.width - SIDEBAR_WIDTH + 10, w.height - 110)
    s2.draw()

################################################################
#                          on resize                           #
################################################################

@w.event
def on_resize(width, height):
    sb_bg.set_pos(width-SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, height)

################################################################
#                     on mouse scroll                          #
################################################################

@w.event
def on_mouse_scroll(x, y, dx, dy):
    if not touching(x, y, 0, 0, sb_bg.bg.x, sb_bg.bg.y, sb_bg.bg.width, sb_bg.bg.height):
        global camera_stable_x, camera_stable_y
        if 65505 in keys.keys() and keys[65505]:
            camera_stable_x -= 10*dy
        else:
            camera_stable_y -= 10*dy

################################################################
#                       on mouse drag                          #
################################################################

@w.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global drag_start_x, drag_start_y, camera_x, camera_y
    if drag_start_x and drag_start_y:
        camera_x = x - drag_start_x
        camera_y = y - drag_start_y
    else:
        if s2.chosen == 0:
            click(x, y)
        else:
            select_rect.width = x - select_rect.x
            select_rect.height= y - select_rect.y

################################################################
#                     on mouse press                           #
################################################################

@w.event
def on_mouse_press(x, y, buttons, modifiers):
    if not touching(x, y, 0, 0, sb_bg.bg.x, sb_bg.bg.y, sb_bg.bg.width, sb_bg.bg.height):
        if modifiers == 18:   # if holding CTRL
            global drag_start_x, drag_start_y
            drag_start_x = x
            drag_start_y = y
        else:
            global select_drag_x, select_drag_y
            if s2.chosen == 0:
                click(x, y)
            else:
                select_drag_x = x
                select_drag_y = y
                select_rect.x = x
                select_rect.y = y
                select_rect.height= 0
                select_rect.width = 0
                select_rect.opacity = 100
    else:
        for bl in block_types:
            if touching(x, y, 0, 0, bl.draw_x, bl.draw_y, bl.sprite.width, bl.sprite.height):
                global active_block
                active_block = bl
                break
        s1.check(x, y)
        s2.check(x, y)

################################################################
#                      on mouse release                        #
################################################################

@w.event
def on_mouse_release(x, y, buttons, modifiers):
    global drag_start_x, drag_start_y
    global camera_y, camera_x, camera_stable_y, camera_stable_x
    global select_drag_x, select_drag_y
    if drag_start_x and drag_start_y:
        camera_stable_x = camera_stable_x + camera_x
        camera_stable_y = camera_stable_y + camera_y
        camera_x = 0
        camera_y = 0
    drag_start_x = None
    drag_start_y = None
    select_rect.opacity = 0
    if select_drag_x and select_drag_y:
        if s2.chosen:
            match s1.chosen:
                case 0:
                    select_build(x, y, select_drag_x, select_drag_y)
                case 2:
                    select_delete(x, y, select_drag_x, select_drag_y)
            select_drag_x = None
            select_drag_y = None

################################################################
#                       on key press                           #
################################################################

@w.event
def on_key_press(symbol, modifiers):
    global blocks
    keys[symbol] = True
    if symbol == pyglet.window.key.E and modifiers == 18:
        a = easygui.filesavebox("Export:", "Export:", "level.ble", [["*.ble", "Bombic level"]])
        export_1(a, blocks)

    if symbol == pyglet.window.key.O and modifiers == 18:
        a = easygui.fileopenbox("Open:", "Open:", "*.ble", [["*.ble", "Bombic level"]])
        blocks = import_1(file)


@w.event
def on_key_release(symbol, modifiers):
    keys[symbol] = False

################################################################
#                           export                             #
################################################################

def export_1(file, data):
    open(file, "w").writelines([f"{x[0]}   {x[1]}   {x[2].id}\n" for x in data])

################################################################
#                            run                               #
################################################################

pyglet.app.run()
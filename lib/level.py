import pyglet
from lib.window import w


BLOCK_SIZE = 50


def collision(x1:int = 0, y1:int = 0, w1:int = 0, h1:int = 0, x2:int = 0, y2:int = 0, w2:int = 0, h2:int = 0):
    return x1 + w1 > x2 and x2 + w2 > x1 and y1 + h1 > y2 and y2 + h2 > y1



class Info:
    def __init__(self, code:str):
        self.info = self.get_info(code)
        if not self.info: raise ValueError("single.dat doesn't contain count of levels on the first line")

    def get_info(self, code:str):
        with open("levels/single.dat", "r", encoding="utf-8") as single:

            # single.dat is in format:
            #  LEVEL_NAME  LEVEL_PATH  DEATH_IMAGE  DEATH_MESSAGE  COMPLETION_IMAGE  COMPLETION_MESSAGE

            try:    _levels = int(single.readline())
            except: return False

            for _ in range(_levels):
                # find and return a matching line in `single.dat`
                row = self._split(single.readline())
                if row and row[0] == code: return row

        with open("levels/single.dat", "r", encoding="utf-8") as single:
            # if no mathing level code return the first level
            if int(single.readline()) > 0: return self._split(single.readline())
            else: return False

    @staticmethod
    def _split(row:str): return [x.strip("\n") for x in row.split(" ") if x]



class Level:
    GROUPS_PER_Y_LAYER = 4

    def __init__(self, file:str, batch:pyglet.graphics.Batch, parent):
        self.source = file
        self.screen = parent
        self.data = {}
        self.b = batch
        self.speed = 1  # speed modifier
        self.blocks:set[Block] = set()
        self.z_groups = []
        self.get_data()

    def get_data(self):
        with open("levels/" + self.source, "r", encoding="utf-8") as data:
            lines = data.readlines()
            for n, i in enumerate(lines):
                if i[0] != "#": raise ValueError("Wrong level format!")

                key, value = i[1:].split(":")
                if key == "dataset": break
                
                self.data[key] = self._trim(value)

            for y, row in enumerate(lines[n+1:]):
                for x, block in enumerate(self._trim(row)):
                    if len(self.z_groups) <= y * self.GROUPS_PER_Y_LAYER:
                        self.z_groups.extend([pyglet.graphics.Group(self.GROUPS_PER_Y_LAYER * y + q) for q in range(self.GROUPS_PER_Y_LAYER)])
                    self.blocks.add(Block(self, x = x, y = y, z = y, identifier = block))

    def _trim(self, line:str): return line.strip("\n")

    def draw(self): self.b.draw()

    def get_collision(self, x:int, y:int, width:int, height:int):
        return [(i, i.collide(x, y, width, height)[1]) for i in self.blocks if i.collide(x, y, width, height)[0]]



class BlockType:
    types = [
        # passable | destructible | dangerous
        (True,  False, False), # ground
        (False, False, False), # rock
        (False, True,  False), # barrel
        (True,  False, True)   # fire
    ]

    def __init__(self, symbol:str, coords:tuple[int], block_type:int=0):
        self.symbol       = symbol
        self.coords       = coords
        self.x, self.y    = coords
        self._p = self.passable     = self.types[block_type][0]
        self._d = self.destructible = self.types[block_type][1]
        self.dangerous              = self.types[block_type][2]

    def restore(self):
        self.destructible = self._d
        self.passable     = self._p



class Block:
    spritesheets = [
        pyglet.image.ImageGrid(pyglet.image.load("img/ground/g1.png"), 4, 10),
        pyglet.image.ImageGrid(pyglet.image.load("img/ground/g2.png"), 4, 10),
        pyglet.image.ImageGrid(pyglet.image.load("img/ground/g3.png"), 4, 10),
        pyglet.image.ImageGrid(pyglet.image.load("img/ground/g4.png"), 4, 10)
    ]

    codes = {
        " ": BlockType(" ", (0, 0), 0),
        "|": BlockType(" ", (1, 0), 1),
        ",": BlockType(" ", (2, 0), 1),
        "_": BlockType(" ", (3, 0), 1),
        ".": BlockType(" ", (4, 0), 1),
        "!": BlockType(" ", (5, 0), 1),
        "`": BlockType(" ", (6, 0), 1),
        "-": BlockType(" ", (7, 0), 1),
        "ˇ": BlockType(" ", (8, 0), 1),
        "O": BlockType(" ", (9, 0), 1),
        "B": BlockType(" ", (4, 1), 2)
    }

    overlay_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

    def __init__(self, level:Level, x:int, y:int, z:int = 0, identifier:str = " ", burn_time:float = 0.5):
        self.level = level
        self.x = x * BLOCK_SIZE
        self.y = y * BLOCK_SIZE
        self.z = z
        # the higher the object is on the screen, the lower would it display (would be overlaid by lower blocks)
        self.corner_size = 18
        # size of align-corners
        self.symbol = identifier
        self.type = self.codes[self.symbol]
        self.passable = self.type.passable
        _pos = self.type.coords
        self.burn_phase = 0
        self.dangerous = False
        self.burn_time = burn_time

        self.image = self.spritesheets[int(self.level.data["theme"]) - 1][10 * (3 - _pos[1]) + _pos[0]]
        self.sprite = pyglet.sprite.Sprite(self.image, x = self.x, y = w.height - self.y - 2*BLOCK_SIZE,
                                           batch = self.level.b, group = self.level.z_groups[self.z*self.level.GROUPS_PER_Y_LAYER])
        self.overlay = pyglet.shapes.Rectangle(x = self.x, y = w.height - self.y - 2*BLOCK_SIZE, width = BLOCK_SIZE, height = BLOCK_SIZE,
                                           batch = self.level.b, group = self.level.z_groups[self.z*self.level.GROUPS_PER_Y_LAYER + 1])
        self.overlay.opacity = 0

    def collide(self, x, y, width, height):
        # collision_full    = (self.x + BLOCK_SIZE > x   and   x + width > self.x)   and   (self.y + BLOCK_SIZE > y   and   y + height > self.y)
        collision_full = collision(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE, x, y, width, height)
        collision_mid  = collision(self.x, self.y + self.corner_size, BLOCK_SIZE, BLOCK_SIZE - 2 * self.corner_size, x, y, width, height) or collision(self.x + self.corner_size, self.y, BLOCK_SIZE - 2 * self.corner_size, BLOCK_SIZE, x, y, width, height)
        collision_type = ("full" if collision_mid else ("align" if collision_full else "none")) if not self.type.passable else "none"
        return (collision_full, collision_type)
    
    def destroy(self):
        pyglet.clock.schedule_interval(self.burn, 0.1)
        self.type = self.codes[" "]
        self.passable = self.type.passable
        self.dangerous = True
        pyglet.clock.schedule_once(self.burn_out, self.burn_time)

    def burn_out(self, dt:int = 0): self.dangerous = False

    def burn(self, *_):
        self.burn_phase += 1
        self.image = self.spritesheets[int(self.level.data["theme"]) - 1][24 + self.burn_phase]
        self.sprite.image = self.image
        if self.burn_phase == 5:
            pyglet.clock.unschedule(self.burn)

    def blink(self, color:int):
        self.overlay.opacity = 25   # ~ 10% of 255
        self.overlay.color = self.overlay_colors[color]

    def stop_blinking(self): self.overlay.opacity = 0


class Upgrade:
    pass
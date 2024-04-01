import pyglet, time
from lib.window import w
from lib.level  import BLOCK_SIZE, Level, Block

class Player:
    _controls = [
        {"UP"   :"up",    "DOWN" :"down",    "LEFT" :"left",    "RIGHT":"right",    "RCTRL":"bomb"},
        {"W"    :"up",    "S"    :"down",    "A"    :"left",    "D"    :"right",    "LCTRL":"bomb"},
        {"I"    :"up",    "K"    :"down",    "J"    :"left",    "L"    :"right",    "SPACE":"bomb"},
        {"NUM_8":"up",    "NUM_5":"down",    "NUM_4":"left",    "NUM_6":"right",    "NUM_0":"bomb"}
    ]
    _directions = {"up": [0,-1], "down": [0,1], "left": [-1,0], "right": [1,0]}

    def __init__(self, color:int, level:Level, batch:pyglet.graphics.Batch = None, start_x:int = 0, start_y:int = 0, animation_speed:float = 10):
        self.type = color
        self.controls = self._controls[color]
        self.spritesheets = {
            "death": pyglet.image.ImageGrid(   pyglet.image.load(f"img/sprites/b{str(color)}.png")   .get_region(0,   0, 458, 70)   , 1, 9, row_padding=1, column_padding=1),
            "down":  pyglet.image.ImageGrid(   pyglet.image.load(f"img/sprites/b{str(color)}.png")   .get_region(0,  71, 458, 70)   , 1, 9, row_padding=1, column_padding=1),
            "up":    pyglet.image.ImageGrid(   pyglet.image.load(f"img/sprites/b{str(color)}.png")   .get_region(0, 142, 458, 70)   , 1, 9, row_padding=1, column_padding=1),
            "right": pyglet.image.ImageGrid(   pyglet.image.load(f"img/sprites/b{str(color)}.png")   .get_region(0, 213, 458, 70)   , 1, 9, row_padding=1, column_padding=1),
            "left":  pyglet.image.ImageGrid(   pyglet.image.load(f"img/sprites/b{str(color)}.png")   .get_region(0, 284, 458, 70)   , 1, 9, row_padding=1, column_padding=1)
        }
        self.batch = batch
        self.alive = True
        self.display = True
        self.pressed = []
        self.level = level
        self.direction = "down"
        self.current_animation_frame = 0
        self.animation_step = 20 / animation_speed
        self._step = 0
        self.moving = False
        self.x, self.y = start_x, start_y
        self.speed = 3 # block per second
        self.bombs = []
        self.sprite = pyglet.sprite.Sprite(self.spritesheets[self.direction][0], batch=batch)
        self.upgrades = {"bombs":1, "fires":1, "shoes":0}
        
        self.update_pos()
        self.update_z()

    def update(self, time:float):
        # moving
        if self.alive:
            if not int(self._step % self.animation_step) and self.moving: self.current_animation_frame += 1
            self.sprite.image = self.spritesheets[self.direction][self.current_animation_frame % 9]
            self._step += 1
            self.update_z()
            if self.moving: self.move(*self._directions[self.direction], self.speed * time * BLOCK_SIZE)

        # burning
        else:
            if not int(self._step % self.animation_step): self.current_animation_frame += 1
            self.sprite.image = self.spritesheets[self.direction][self.current_animation_frame]
            self._step += 1
            if self.current_animation_frame > 7: self.die()

    def on_animation_start(self):
        self.current_animation_frame = 0
        self.moving = True

    def on_animation_end(self):
        self.current_animation_frame = 0
        self.moving = False

    def press(self, key:str):
        if self.alive and key in self.controls.keys():
            k = self.controls[key]
            if k == "bomb":
                ax = round(self.x / BLOCK_SIZE) * BLOCK_SIZE
                ay = round(self.y / BLOCK_SIZE) * BLOCK_SIZE
                if not (ax, ay) in [(b.x, b.y) for b in Bomb.instances]:
                    self.place_bomb(ax, ay)
            else:
                self.direction = k
                self.on_animation_start()

    def release(self, key:str):
        if key in self.controls.keys() and self.controls[key] == self.direction: self.on_animation_end()

    def update_z(self): self.sprite.group = self.level.z_groups[self.level.GROUPS_PER_Y_LAYER * ((self.y - 8) // BLOCK_SIZE + 1) + 3]

    def update_pos(self): self.sprite.x, self.sprite.y = self.x, w.height - 2 * BLOCK_SIZE - self.y

    def move(self, dx:int = 0, dy:int = 0, multiplier:float = 0):
        if dx:
            _x_diff = dx * multiplier * self.level.speed
            _collision_x_1 = self.level.get_collision(self.x,           self.y, BLOCK_SIZE, BLOCK_SIZE) # actual collision
            _collision_x_2 = self.level.get_collision(self.x + _x_diff, self.y, BLOCK_SIZE, BLOCK_SIZE) # collision after the movement
            _collision_x_diff = [b for b in _collision_x_2 if b not in _collision_x_1] # differences in the lists

            if False in [b[0].passable for b in _collision_x_diff]:
                # if the block is solid
                _ctypes = [b[1] for b in _collision_x_diff]
                x_diff = _collision_x_diff[0][0].x - self.x
                self.x += x_diff - x_diff // abs(x_diff) * BLOCK_SIZE
                # move right in front of the block
                if not "full" in _ctypes and "align" in _ctypes:
                    # corner collision: align player y
                    b = _collision_x_diff[_ctypes.index("align")][0]
                    dy = b.y + BLOCK_SIZE - self.y if self.y > b.y else b.y - BLOCK_SIZE - self.y
                    self.y += dy
            else:
                # if it is not solid
                self.x += int(dx * multiplier)
                # move player by `self.speed` px
        
        elif dy:
            _y_diff = dy * multiplier * self.level.speed
            _collision_y_1 = self.level.get_collision(self.x, self.y,           BLOCK_SIZE, BLOCK_SIZE) # actual collision
            _collision_y_2 = self.level.get_collision(self.x, self.y + _y_diff, BLOCK_SIZE, BLOCK_SIZE) # collision after the movement
            _collision_y_diff = [b for b in _collision_y_2 if b not in _collision_y_1] # differences in the lists

            if False in [b[0].passable for b in _collision_y_diff]:
                # if the block is solid
                _ctypes = [b[1] for b in _collision_y_diff]
                y_diff = _collision_y_diff[0][0].y - self.y
                self.y += y_diff - (y_diff // abs(y_diff)) * BLOCK_SIZE
                # move right in front of the block
                if not "full" in _ctypes and "align" in _ctypes:
                    # corner collision: align player x
                    b = _collision_y_diff[_ctypes.index("align")][0]
                    dx = b.x + BLOCK_SIZE - self.x if self.x > b.x else b.x - BLOCK_SIZE - self.x
                    self.x += dx
            else:
                # if it is not solid
                self.y += int(dy * multiplier)
                # move player by `self.speed` px

        self.check_death()

        self.update_pos()

    def place_bomb(self, x:int = 50, y:int = 50):
        self.bombs.append(Bomb(x, y, self.upgrades["fires"], self.level, self.batch))

    def check_death(self):
        if Fire.touch(self) or True in [b.dangerous for b, c in self.level.get_collision(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)]:
            self.burn()

    def burn(self):
        self.alive = False
        self._step = 0
        self.moving = False
        self.direction = "death"

    def die(self): self.display = False



class Bomb:
    TICK_INTERVAL = 0.1
    EXPLOSION_DELAY = 2
    FIRE_DURATION = 0.5

    instances = set()
    _blink_stage = 0
    spritesheet = pyglet.image.ImageGrid(pyglet.image.load("img/sprites/explosion.png").get_region(0, 248, 356, 50), 1, 7, column_padding = 1)

    def __init__(self, x:int, y:int, reach:int, level:Level, batch:pyglet.graphics.Batch):
        self.level = level
        self.reach = reach
        self.x, self.y = round(x), round(y)
        self.rx, self.ry = self.x // BLOCK_SIZE * BLOCK_SIZE, self.y // BLOCK_SIZE * BLOCK_SIZE
        self.start_blink = self._blink_stage
        self.start = time.time()

        # find bomb's base block
        self.block = self.level.get_collision(self.x + 1, self.y + 1, 1, 1)[0][0]
        # total impact, remove duplicate (center point) by using set
        self.impact:set[Block] = set(
            [self.find(self.x + _x * BLOCK_SIZE, self.y) for _x in range(-self.reach, self.reach + 1)] +
            [self.find(self.x, self.y + _y * BLOCK_SIZE) for _y in range(-self.reach, self.reach + 1)]
        )

        self.fire_slots:set[Block] = set()
        self.destroy_slots = set()
        self.calc()

        self.sprite = pyglet.sprite.Sprite(self.spritesheet[0], self.x, w.height - 2 * BLOCK_SIZE - self.y, batch = batch,
                        group = self.level.z_groups[self.level.GROUPS_PER_Y_LAYER * ((self.y - 10) // BLOCK_SIZE + 1) + 2])

        self.instances.add(self)

    def find(self, x:int, y:int) -> Block:
        """ Get block by position """
        return self.level.get_collision(x + 1, y + 1, 1, 1)[0][0]

    def check(self, timestamp:float) -> bool:
        """ Check if this bomb should explode now """
        if timestamp >= self.start + self.EXPLOSION_DELAY: return True

    def explode(self) -> None:
        """ Execute the explosion and delete the sprite """
        for i in self.fire_slots: i.stop_blinking()
        for i in self.destroy_slots: i.destroy()
        self.sprite.delete()
        self.instances.remove(self)
        del self

    def find_impact(self) -> list:
        """ Return all bombs affected by this bomb's explosion """
        return [b for b in self.instances if (b.x, b.y) in [(i.x, i.y) for i in self.fire_slots]]

    def calc(self) -> None:
        """ Recalculate `fire_slots` and `destroy_slots` """
        # impact on passable blocks (blinking)
        self.fire_slots = set([b for b in self.impact if b.type.passable])
        # impact on destructible blocks (destroying)
        self.destroy_slots = set([b for b in self.impact if b.type.destructible])

    @classmethod
    def _find_explosion(cls, explosion:list|set) -> list:
        old:list[Bomb] = explosion
        n = [e.find_impact() for e in old]
        new = list(set([i for row in n for i in row]))  # convert 2d list to 1d
        if old == new:
            return new
        else:
            return cls._find_explosion(new)
        
    @classmethod
    def tick(cls):
        for b in cls.instances:
            for i in b.fire_slots:
                i.blink(cls._blink_stage % 3)
        
        cls._blink_stage += 1

        now = time.time()

        # get all bombs to explode and all impacted
        explode:list[Bomb] = cls._find_explosion([b for b in cls.instances if b.check(now)])

        # generate fire
        if explode:
            level = explode[0].level
            Fire.create(explode)

        for i in explode: i.explode()
        
        # recalculate the other bomb's fire and impact
        if explode:
            for b in cls.instances: b.calc()
            for p in level.screen.players:
                p.check_death()



class Fire:
    spritesheet = pyglet.image.ImageGrid(pyglet.image.load("img/sprites/explosion.png").get_region(0, 299, 356, 153), 3, 7, row_padding=1, column_padding=1)
    instances = set()
    _phase = 0

    def __init__(self, x:int, y:int, now:float, shape:int = 3, duration:float = 0.5, batch:pyglet.graphics.Batch = None, group:pyglet.graphics.Group = None):
        self.x = x
        self.y = y
        self.shape = shape  # 3 is the corner one
        self.start = now
        self.duration = duration

        self.sprite = pyglet.sprite.Sprite(self.spritesheet[self.shape], self.x, w.height - 2 * BLOCK_SIZE - self.y, batch = batch, group = group)

    def update(self, current_time):
        self.sprite.image = self.spritesheet[7 * self._phase + self.shape]
        return current_time >= self.start + self.duration

    def end(self):
        self.sprite.delete()
        self.instances.remove(self)
        del self

    def collides(self, object:Player|Block):
        return self.x + BLOCK_SIZE > object.x and object.x + BLOCK_SIZE > self.x and self.y + BLOCK_SIZE > object.y and object.y + BLOCK_SIZE > self.y

    @classmethod
    def tick(cls):
        now = time.time()
        for d in [i for i in cls.instances if i.update(now)]: d.end()
        cls._phase = (cls._phase + 1) % 3

    @classmethod
    def find(cls, x:int, y:int):
        """ Return if there is already a fire object on given position """
        return bool([1 for i in cls.instances if i.x == x and i.y == y])
    
    @classmethod
    def make(cls, x:int = 0, y:int = 0, now:float = 0, shape:int = 3, duration:float = 0.5, batch:pyglet.graphics.Batch = None, group:pyglet.graphics.Group = None):
        """ Create a `Fire` object if it doesn't exist """
        if not cls.find(x, y): cls.instances.add(Fire(x, y, now, shape, duration, batch, group))

    @classmethod
    def touch(cls, player:Player):
        return [i for i in cls.instances if i.collides(player)]

    @staticmethod
    def create(explosions:set[Bomb]):
        """ Create a `Fire` objects from `Bomb`s """
        now = time.time()
        for e in explosions:
            for b in e.fire_slots:
                Fire.make(b.x, b.y, now = now, shape = 3, duration = 0.5, batch = b.level.b, group = b.level.z_groups[b.level.GROUPS_PER_Y_LAYER * ((b.y - 10) // BLOCK_SIZE + 1) + 1])
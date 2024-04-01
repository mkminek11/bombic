import pyglet, math
from pyglet.window import key as k

from lib.event import Event


ELEMENT_ACTIVE_COLOR   = (255, 255, 255, 255)
ELEMENT_INACTIVE_COLOR = (150, 150, 150, 255)


class Element:
    def __init__(self):
        self.b = pyglet.graphics.Batch()
        # self._mouse_on    = False
        # self._mouse_press = False
        self.element:pyglet.shapes.Rectangle|pyglet.text.Label|pyglet.image.AbstractImage
        self.event = Event()

    def draw(self): self.b.draw()

    # def collide(self, x:int, y:int):
    #     try:    return (x >= self.element.x and x <= self.element.x + self.element.width)         and (y >= self.element.y and y <= self.element.y + self.element.height)
    #     except: return (x >= self.element.x and x <= self.element.x + self.element.content_width) and (y >= self.element.y and y <= self.element.y + self.element.content_height)

    # def on_mouse_on    (self): pass
    # def on_mouse_over  (self): pass
    # def on_mouse_press (self): pass

    def center_x(self, window:pyglet.window.Window):
        try:    self.element.x = window.width  // 2 - self.element.content_width  // 2
        except: self.element.x = window.width  // 2 - self.element.width          // 2
    
    def center_y(self, window:pyglet.window.Window):
        try:    self.element.y = window.height // 2 - self.element.content_height // 2
        except: self.element.y = window.height // 2 - self.element.height         // 2

    def on_focus (self): self.element.color = ELEMENT_ACTIVE_COLOR
    def on_blur  (self): self.element.color = ELEMENT_INACTIVE_COLOR
    def on_submit(self): return self.event
    def on_text  (self, key, modifiers, window): pass


class Link(Element):
    def __init__(self, text:str, event:Event, x:int = 0, y:int = 0, font_size:int = 40, batch:pyglet.graphics.Batch = None, **kwargs):
        super().__init__()
        self.event = event
        self.element = pyglet.text.Label(text, x=x, y=y, font_size=font_size, batch=batch, **kwargs)
        self.on_blur()


class Text(Element):
    def __init__(self, text:str, x:int = 0, y:int = 0, font_size:int = 40, batch:pyglet.graphics.Batch = None, **kwargs):
        super().__init__()
        self.element = pyglet.text.Label(text, x=x, y=y, font_size=font_size, batch=batch, **kwargs)
        self.on_blur()


class NumSwitch(Element):
    def __init__(self, window:pyglet.window.Window, text:str = "", x:int = 0, y:int = 0, font_size:int = 40,
                    output_y:int = 0, output_padding:int = 20, output:list[pyglet.sprite.Sprite] = [],
                    nmin:int = 1, nmax:int = 4, batch:pyglet.graphics.Batch = None):
        
        super().__init__()
        if len(output) != nmax - nmin + 1: raise ValueError("Outputs don't match the given range")

        self.element = pyglet.text.Label(text, font_size=font_size, x=x, y=y, batch=batch)
        self.outputs = output
        for i in self.outputs:
            i.y = output_y
            try: i.anchor_position = (-i.radius, -i.radius)
            except: pass
        self.w = window
        self.nmin = nmin
        self.nmax = nmax
        self.value = nmin
        self.data = {"y": output_y, "s": output_padding}
        self.update()
        self.on_blur()

    def next(self):
        self.value += 1
        if self.value > self.nmax: self.value = self.nmin
        self.update()

    def prev(self):
        self.value -= 1
        if self.value < self.nmin: self.value = self.nmax
        self.update()

    def update(self):
        show = self.outputs[:self.value]
        width = - self.data["s"]

        for n, i in enumerate(self.outputs):
            if n + 1 <= self.value:
                try: elw = i.width
                except:
                    try: elw = 2*i.radius
                    except: elw = i.content_width
                i.opacity = 255
                width += self.data["s"] + elw
            else:
                i.opacity = 0

        x = self.w.width // 2 - width // 2
        for i in show:
            try: elw = i.width
            except:
                try: elw = 2*i.radius
                except: elw = i.content_width

            i.x = x
            x += elw + self.data["s"]

    def on_submit(self):
        self.next()
        return Event()

    def on_text(self, key, modifiers, window):
        if   key in [k.SPACE, k.ENTER, k.RIGHT]: self.next()
        elif key in [k.LEFT]:                    self.prev()


class Input(Element):
    def __init__(self, text:str="", x:int = 0, y:int = 0, font_size:int = 40, maxsize:int = math.inf, batch:pyglet.graphics.Batch = None,
                    nonumbers:bool = False, uppercase:bool = False, **kwargs):
        super().__init__()

        self.text = text
        self.value = ""
        self.maxsize = maxsize
        self.settings = {"nonumbers": nonumbers, "uppercase": uppercase}
        self.element = pyglet.text.Label(text, x=x, y=y, font_size=font_size, batch=batch, **kwargs)
        self.on_blur()

    def on_text(self, key, modifiers, window):
        symbol = pyglet.window.key.symbol_string(key)

        # if len(self.value) >= self.maxsize: return

        if len(symbol) == 1:
            # If the symbol is alphabetical
            self._add(symbol)
        elif not self.settings["nonumbers"] and len(symbol) == 2 and symbol[0] == "_":
            # If supports numbers and the symbol is numerical
            self._add(symbol)
        elif symbol == "BACKSPACE":
            
            # If the symbol is backspace
            self.value = self.value[:-1]

        self.element.text = self.text + self.value
        self.center_x(window)

    def _add(self, letter):
        if len(self.value) < self.maxsize: self.value += letter


class Image(Element):
    def __init__(self, image:pyglet.image.AbstractImage, x:int = 0, y:int = 0, width:int = 100, height:int = 100,
                    stretch:bool = False, batch:pyglet.graphics.Batch = None, group:pyglet.graphics.Group = None):
        super().__init__()
        self.image = image
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sprite = pyglet.sprite.Sprite(image, x, y, batch = batch, group = group)

        self.stretch = stretch    # has two modes: stretch (True), crop (False)
        # find which axis to crop:   0 = x, 1 = y
        self.crop = 0 if width / image.width * image.height < height else 1

        if self.stretch:
            self.sprite.scale_x = self.width  / self.sprite.width
            self.sprite.scale_y = self.height / self.sprite.height
        else:
            self.sprite.scale = [width, height][self.crop] / [self.sprite.height, self.sprite.width][self.crop]
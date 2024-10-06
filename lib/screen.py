import pyglet
from lib import elements, event, level, player
from lib.logs import *

MenuType   = "bombic.screentype.menu"
InfoType   = "bombic.screentype.info"
GameType   = "bombic.screentype.game"
EditorType = "bombic.screentype.ble"


class Screen:
    def __init__(self):
        self.type = None
        self.b = pyglet.graphics.Batch()
        self.exit_event = event.Event(action = event.EXIT)

    def draw(self): self.b.draw()
    
    def exit(self):
        """ When user hits Escape """
        return self.exit_event


class MenuScreen(Screen):
    def __init__(self):
        super().__init__()
        self.type = MenuType
        self.focus = -1
        self.elements:list[elements.Element] = []
        self.dynamic :list[elements.Element] = []

    def focus_down(self):
        """ When user hits Arrow down """
        self.dynamic[self.focus].on_blur()
        self.focus = (self.focus - 1) % len(self.dynamic)
        self.dynamic[self.focus].on_focus()

    def focus_up(self):
        """ When user hits Arrow up """
        self.dynamic[self.focus].on_blur()
        self.focus = (self.focus + 1) % len(self.dynamic)
        self.dynamic[self.focus].on_focus()

    def submit(self):
        """ When user hits Enter or Space """
        return self.dynamic[self.focus].on_submit()

    def key(self, key:int, modifiers:int, window:pyglet.window.Window):
        """ When user hits a key """
        self.dynamic[self.focus].on_text(key, modifiers, window)

    def draw(self):
        if self.dynamic: self.dynamic[self.focus].on_focus()
        super().draw()


class InfoScreen(Screen):
    def __init__(self, window:pyglet.window.Window, labels:list[elements.Text] = [], background:elements.Image = None):
        super().__init__()
        self.type = InfoType
        self.exit_event = event.Event(redirect = StoryMenu)




# Main menu
class MainMenu(MenuScreen):
    def __init__(self, window:pyglet.window.Window):
        super().__init__()

        _links = [
            ("Příběh",    event.Event(redirect = StoryMenu)),
            ("Dedmeč",    event.Event(redirect = DeadmatchMenu)),
            ("Mrchovník", event.Event(redirect = WIPMenu)),
            ("Editor",    event.Event(redirect = LevelEditor)),
            ("Ukončit",   event.Event(action = event.EXIT)),
        ]

        self.elements = self.dynamic = [elements.Link(text, event, y=300 + 100*y, font_size=40, batch=self.b) for y, (text, event) in enumerate(reversed(_links))]

        for l in self.elements: l.center_x(window)


# Story mode menu
class StoryMenu(MenuScreen):
    def __init__(self, window:pyglet.window.Window):
        super().__init__()
        self.exit_event = event.Event(redirect = MainMenu)

        # _switch_elements = [pyglet.sprite.Sprite(pyglet.image.load(f"img/sprites/b{x}.png").get_region(0, 71, 50, 70), batch=self.b) for x in range(4)]
        _switch_elements = [pyglet.shapes.Circle(0, 0, 50, batch=self.b) for x in range(4)]

        self.elements = self.dynamic = [
            elements.Link("Zpět", event = event.Event(redirect = MainMenu), y = 300, batch = self.b),
            _level   := elements.Input("Level: ", y = 400, maxsize = 6, nonumbers = True, uppercase = True, batch = self.b),
            _players := elements.NumSwitch(window, "Počet hráčů", y = 500, nmin = 1, nmax = 4, output_y = 700, output = _switch_elements, batch = self.b),
            elements.Link("Hrr na ně!", event.Event(redirect = StoryScreen, data = [_level, _players]), y = 600, batch = self.b),
        ]

        for l in self.elements: l.center_x(window)


# Deadmatch menu
class DeadmatchMenu(MenuScreen):
    def __init__(self, window:pyglet.window.Window):
        super().__init__()
        self.exit_event = event.Event(redirect = MainMenu)

        # _switch_elements = [pyglet.sprite.Sprite(pyglet.image.load(f"img/sprites/bomber{x}.png")) for x in range(4)]
        _switch_elements = [pyglet.shapes.Circle(0, 0, 50, batch=self.b) for x in range(4)]

        self.elements = self.dynamic = [
            elements.Link("Zpět", event = event.Event(redirect = MainMenu), y = 300, batch = self.b),
            _level   := elements.Input("Level: ", y = 400, maxsize = 6, nonumbers = True, uppercase = True, batch = self.b),
            _players := elements.NumSwitch(window, "Počet hráčů", y = 500, nmin = 1, nmax = 4, output_y = 700, output = _switch_elements, batch = self.b),
            elements.Link("Hrr na ně!", event.Event(redirect = StoryScreen, data = [_level, _players]), y = 600, batch = self.b),
        ]

        for l in self.elements: l.center_x(window)


# Not completed pages
class WIPMenu(MenuScreen):
    def __init__(self, window:pyglet.window.Window):
        super().__init__()
        self.exit_event = event.Event(redirect = MainMenu)

        self.dynamic = [
            elements.Link("Zpět", event = event.Event(redirect = MainMenu), y = 300, batch = self.b),
        ]

        self.elements = self.dynamic + [elements.Text("Na tomto se právě pracuje.", y = 500, batch = self.b)]

        for l in self.elements: l.center_x(window)


# Before level enter
class StoryScreen(InfoScreen):
    def __init__(self, window:pyglet.window.Window, data:list[elements.Input|elements.NumSwitch|str|int]):
        super().__init__(window)

        _level = data[0] if type(data[0]) == str else data[0].value
        _players = data[1] if type(data[1]) == int else data[1].value

        self.level = level.Info(_level).info
        _code = self.level[0]
        _file = self.level[1]

        self.dynamic = []
        self.elements = [elements.Text(self.level[0], y = 700, batch = self.b)]

        self.data = {
            "players_count": _players,
            "level_code":    _code,
            "level_source":  _file
        }

        for l in self.elements: l.center_x(window)

    def submit(self):
        return event.Event(redirect = MainGame, data = self.data)


# The level screen
class MainGame(Screen):
    DEATH_COUNTDOWN = 1   # return 1 second after all players die

    def __init__(self, window:pyglet.window.Window, data:dict):
        super().__init__()

        self.data = data
        self.type = GameType
        self.players_count = data["players_count"]
        self._source = data["level_source"]
        self.playing = True
        self.returned = False

        self.exit_event = event.Event(redirect = StoryScreen, data = [data["level_code"], self.players_count])

        self.level = level.Level(self._source, self.b, self)
        # player start position
        psx, psy = [int(c) * level.BLOCK_SIZE for c in self.level.data["player_start"][1:-1].split(",")]

        self.players = [player.Player(i, self.level, self.b, psx, psy) for i in range(self.players_count)]
        # schedule players update
        pyglet.clock.schedule_interval(self.update, 0.05)
        # for p in self.players: pyglet.clock.schedule_interval(p.update, 0.05)

    def key(self, symbol:int, modifiers:int, window:pyglet.window.Window):
        key_code = pyglet.window.key._key_names[symbol]
        for p in self.players: p.press(key_code)

    def draw(self):
        super().draw()
        self.level.draw()

    def release(self, symbol:int):
        key_code = pyglet.window.key._key_names[symbol]
        for p in self.players: p.release(key_code)

    def tick(self):
        """ Called 10 times per second from the `main.py` """
        player.Bomb.tick()
        player.Fire.tick()

        if not self.playing and not self.returned:
            self.returned = True
            return self.exit_event


    def update(self, time:float):
        """ Called 20 times per second """
        if self.playing:
            for i in self.players:
                # check if player is alive
                if i.display:
                    i.update(time)
                else:
                    self.players.remove(i)
                    i.sprite.delete()
                    del i

        # check if all players died
        if self.playing and not self.players:
            # end the game
            self.playing = False
            info("You lost")


# Level editor
class LevelEditor(Screen):
    def __init__(self, window:pyglet.window.Window):
        super().__init__()
        self.exit_event = event.Event(redirect = MainMenu)


import pyglet
from pyglet.window import key
from lib import screen
from lib.event import *
from lib.player import *
from lib.window import w

w.set_exclusive_mouse(True)


page = screen.MainMenu(w)


def process(e:Event):
    print(e)
    if e.redirect is not None:
        global page
        page = e.redirect(w) if e.data is None else e.redirect(w, e.data)
    elif e.action == EXIT:
        w.close()


@w.event
def on_draw():
    w.clear()
    page.draw()


@w.event
def on_key_press(symbol, modifiers):
    if page.type == screen.MenuType:
        if   symbol == key.DOWN: page.focus_down()
        elif symbol == key.UP:   page.focus_up()
        elif symbol == key.SPACE or symbol == key.ENTER: process(page.submit())
        elif symbol == key.ESCAPE: process(page.exit())
        else: page.key(symbol, modifiers, w)
    elif page.type == screen.InfoType:
        if symbol == key.SPACE or symbol == key.ENTER: process(page.submit())
        elif symbol == key.ESCAPE: process(page.exit())
    else:
        if symbol == key.ESCAPE: process(page.exit())
        page.key(symbol, modifiers, w)
    
    return pyglet.event.EVENT_HANDLED


@w.event
def on_key_release(symbol, modifiers):
    if page.type == screen.GameType: page.release(symbol)


def tick(ms:int = None):
    Bomb.tick()
    Fire.tick()

pyglet.clock.schedule_interval(tick, Bomb.TICK_INTERVAL)


pyglet.app.run()
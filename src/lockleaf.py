
import screens.main_menu
import curses
import keyboard

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    rows, cols = stdscr.getmaxyx()
    curses.resize_term(rows, cols)
    #keyboard.press('f11')
    screens.main_menu.start()

curses.wrapper(main)
from escpos.printer import Usb

# ESC/POS USB thermal printer
printer = Usb(0x0483, 0x5743)


# printer character limits
char_limit = 48
name_limit = 14
qtys_limit = 8


# basic printer function wrappers
def style(**args): printer.set_with_default(**args)
def repeat(char: str, num: int): printer.text(char * num)


# printer shorthands using repeat
def line(num: int = char_limit): repeat("─", num)
def space(num: int = 1): repeat(" ", num)
def dot(num: int = 1): repeat(".", num)
def next_row(num: int = 1): repeat("\n", num)


# printer passthrough functions
def text(*args): printer.text(*args)
def textln(*args): printer.textln(*args)
def cut(*args): printer.cut(*args)


# other simple printer utilities
def beep(num = 1): printer.buzzer(num, 2)
def boop(num = 1): printer.buzzer(num, 1)

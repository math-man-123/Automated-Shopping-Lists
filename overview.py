from escpos.printer import Usb

# SETTINGS THAT WORK ON MY PRINTER:
# - align="left"/"middle"/"center"
# - bold=True/False (bold text or not)
# - underline=0/1/2 (no, light, dark line)
# - font="a"/"b" (bigger, smaller font)
# - double_width=True [STICKY: RESET TO CLEAR]
# - double_height=True [STICKY: RESET TO CLEAR]
# - density=5/6/7/8 (higher = better quality)
# - invert=True/False (black on white or inverted)
# - flip=True/False (prints as if paper fliped)
#
# SETTINGS THAT DO NOT WORK:
# - widht and height (both fonts don't care)


# get usb printer by its ID
printer = Usb(0x0483, 0x5743)

# printer can make a sound
printer.buzzer(times=1, duration=2)


# RESETS TO DEFAULT VALUES (if not supplied):
# - align="left", bold=False, underline=0, font="a"
# - double_width=False, double_height=False
# - density=9, invert=False, flip=False
#
# also always use this to set specific style as  
# it seems to work best (clears sticky flags etc)
printer.set_with_default()


# older commands used during initial testing 
# i.e. in this file exactly, new: printer.py
def SET(**args): printer.set_with_default(**args)
def PRINT(string=""): printer.textln(string)

def TITLE(string):
    SET(invert=True)
    PRINT(string)


msg = "The quick brown fox."
# -------------------------------------------------------
# DEFAULT STYLE
# -------------------------------------------------------
TITLE("default")
SET()
PRINT(msg)
PRINT()


# -------------------------------------------------------
# ALIGN STYLE
# -------------------------------------------------------
TITLE("align")
for a in ("left", "center", "right"):
    SET(align=a)
    PRINT(f"{a}: {msg}")
PRINT()


# -------------------------------------------------------
# BOLD STYLE
# -------------------------------------------------------
TITLE("bold")
for b in (True, False):
    SET(bold=b)
    PRINT(f"{b}: {msg}")
PRINT()


# -------------------------------------------------------
# UNDERLINE STYLE
# -------------------------------------------------------
TITLE("underline")
for u in (0, 1, 2):
    SET(underline=u)
    PRINT(f"{u}: {msg}")
PRINT()


# -------------------------------------------------------
# FONT A STYLE
# -------------------------------------------------------
TITLE('font="a"')

SET()
PRINT(f"default: {msg}")

SET(double_width=True)
PRINT(f"double_width=True: {msg}")

SET(double_height=True)
PRINT(f"double_height=True: {msg}")

SET(double_width=True, double_height=True)
PRINT(f"both: {msg}")

PRINT()


# -------------------------------------------------------
# FONT B STYLE
# -------------------------------------------------------
TITLE('font="b"')

SET(font="b")
PRINT(f"default: {msg}")

SET(font="b", double_width=True)
PRINT(f"double_width=True: {msg}")

SET(font="b", double_height=True)
PRINT(f"double_height=True: {msg}")

SET(font="b", double_width=True, double_height=True)
PRINT(f"both: {msg}")


# printer can cut the paper
printer.cut()

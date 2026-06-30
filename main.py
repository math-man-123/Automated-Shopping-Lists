from gpiozero import DigitalOutputDevice
import printer


# setup printer power relay and activate it
printer_relay = DigitalOutputDevice(27, active_high=False)
printer_relay.on()


from file_reader import load_json, check_id
from gpiozero import Button
from shopping_list import ShoppingList
import camera, time, os


# setup power, delete, print button as interrupts
bounce_time = 0.05; hold_time = 0.5
power_btn = Button(3, bounce_time=bounce_time, hold_time=hold_time)
delete_btn = Button(4, bounce_time=bounce_time, hold_time=hold_time)
print_btn = Button(17, bounce_time=bounce_time)


# global cache and flags
recipe_ids = []
debug = False
shutdown = False


# idle timer (shutdown after 3 min)
max_inactive = 60 * 3
last_action = time.monotonic()
if debug: print(last_action)


def delete_last() -> None:
    """Delete last recipe id from recipe_ids cache."""
    global debug, recipe_ids
    if debug: print("delete_last")
    
    # if recipe_ids cache is not empty
    # confirm action and pop last id
    if not recipe_ids: return
    printer.boop(); recipe_ids.pop()

    # update last action time
    last_action = time.monotonic()

# setup delete callback
delete_btn.when_released = delete_last


def delete_all() -> None:
    """Delete all recipe ids from recipe_ids cache."""
    global debug, recipe_ids
    if debug: print("delete_all")

    # if recipe_ids cache is not empty
    # confirm action and clear full cache
    if not recipe_ids: return
    printer.boop(2); recipe_ids = []

    # update last action time
    last_action = time.monotonic()

# setup delete callback
delete_btn.when_held = delete_all


def print_list() -> None:
    """Create and immediately print list from cache."""
    global debug, recipe_ids
    if debug: print("print_list")

    # if recipe_ids cache is 
    # not empty confirm action
    if not recipe_ids: return
    printer.boop()

    # create new shopping list, load each
    # recipie via id, and add them to list
    shopping_list = ShoppingList()
    for recipie_id in recipe_ids:
        recipie = load_json(recipie_id)
        shopping_list.add_recipe(recipie)
    
    # print the list and clear the cache
    shopping_list.print(); recipe_ids = []

    # update last action time
    last_action = time.monotonic()

# setup print callback
print_btn.when_released = print_list


def flag_shutdown() -> None:
    """Set shutdown flag to True causing main loop to exit."""
    global debug, shutdown
    if debug: print("flag_shutdown")

    # confirm action and set shutdown flag
    printer.boop(2); shutdown = True

# setup shutdown callback
power_btn.when_held = flag_shutdown


while True:
    # exit if idle time too long or shutdown is set
    delta = time.monotonic() - last_action
    if (delta > max_inactive) or shutdown: break

    # try to scan valid qrcode, continue if fail
    recipie_id = camera.scan_qrcode()
    if not recipie_id: continue
    if not check_id(recipie_id): continue
    
    # update last action time
    last_action = time.monotonic()
        
    # add recipie_id to recipie_ids cache and wait
    # a bit so the user can remove the card    
    if debug: print(recipie_id)    
    recipe_ids.append(recipie_id)
    time.sleep(0.5)


# power off printer and shutdown pi
printer_relay.off()
if debug: print("shutdown")
else: os.system("sudo shutdown -h now")

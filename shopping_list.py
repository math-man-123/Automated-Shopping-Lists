from collections import defaultdict
from file_reader import load_json
from datetime import date
import printer


# section data from file and all known units
section_data = load_json("section_data")
units = ["", "g", "kg", "ml", "l", "TL", "EL", "?"]


class ShoppingList:
    def __init__(self, seperator = "/") -> None:
        """Create a new shopping list with no added recipes."""
        # section: name, items
        self._sections = defaultdict(list)
        self._date = date.today().strftime("%d-%m-%Y")
        self._seperator = seperator

        # setup column toggle for item print
        self._col = 0


    def _print_section_head(self, name: str) -> None:
        """Print a section head with its `name` and code."""
        # inverted and bold name
        printer.style(invert=True, bold=True)
        printer.text(" " + name + " ")

        # line after section name
        line_len = printer.char_limit
        line_len -= len(name) + 4

        printer.style()
        printer.space()
        printer.line(line_len)

        # reset printer style and skip row
        printer.style()
        printer.next_row(2)


    def _format_qtys(self, qtys: str) -> str:
        """Format `qtys` to take minimum space when priniting."""
        formated = []
        for qty in qtys.split(self._seperator):
            # split quantity to allow conversions
            val, unit = self._split_qty(qty)
            if not val > 0: continue

            # handle "g", "ml" case (may switch unit)
            if unit in ("g", "ml") and val >= 1000:
                unit = "kg" if unit == "g" else "l"
                val /= 1000

            # do not output tailing zeros and only 1 decimal precision
            if val.is_integer(): val = int(val)
            else: val = f"{val:.1f}"

            # rejoin quantity for printing
            formated.append((val, unit))
        
        # sort quantities by unit order
        formated.sort(key=lambda vu: units.index(vu[1]))
        return self._seperator.join([f"{val}{unit}" for val, unit in formated])


    def _print_item(self, name: str, qtys: str) -> None:
        """Print a item its `name` and `qtys`. Handels columns."""
        # clamp name and qtys to limits
        # and also wrap qtys in brackets
        name = name[:printer.name_limit]
        qtys = f"({qtys[:printer.qtys_limit]})"

        # item name
        printer.style()
        printer.text(name)

        # at least one (+1 dot)
        dot_len = printer.name_limit + 1
        dot_len -= len(name)
        printer.dot(dot_len)

        # item qtys
        printer.style(font="b")
        printer.text(qtys)

        # extra brackets (+2 spaces)
        space_len = printer.qtys_limit + 2
        space_len -= len(qtys)
        printer.space(space_len)

        # reset printer style
        printer.style()

        # enter next row if second column
        # else add three spaces
        if self._col: printer.next_row()
        else: printer.space(3)
        self._col ^= 1 # toggle


    def print(self) -> None:
        """Print entire shopping list section by section."""
        # can not sort defaultdict, have to order manually
        sec_order = [
            sec["name"] for sec in section_data 
            if sec["name"] in self._sections]

        # insert overview section at beginning
        sec_order = [self._date] + sec_order

        for sec_name in sec_order:
            # sort each section alphabetically
            alphabet = lambda item: item["name"].lower()
            self._sections[sec_name].sort(key=alphabet)

            # print section head and reset col
            self._print_section_head(sec_name)
            self._col = 0

            # print items (2 per row)
            for item in self._sections[sec_name]:
                # format quantities then split
                qtys = self._format_qtys(item["qtys"])
                qtys = qtys.split(self._seperator)

                # print as many sub items as needed to 
                # fully show all quantities on list
                sub_qtys = ""
                for idx, qty in enumerate(qtys):
                    # build up sub qtys string
                    if not sub_qtys: test_qtys = qty
                    else: test_qtys = sub_qtys + self._seperator + qty
                    
                    # check if string can be expanded
                    # continue if not last quantity
                    if len(test_qtys) <= printer.qtys_limit:
                        sub_qtys = test_qtys; 
                        if idx != len(qtys) - 1: continue
                        
                    # print item with sub qtys string
                    self._print_item(item["name"], sub_qtys)
                    sub_qtys = qty

            # row of whitespace
            printer.next_row(1 + self._col)

        # cut the paper at end
        printer.cut()


    def _split_qty(self, qty: str) -> tuple[float, str]:
        """Split single `qty` into value and unit part. 
        Also convert to base unit (e.g. kg to g)."""
        def is_num(test: str) -> bool:
            """Check if `test` string is number."""
            try: float(test); return True
            except ValueError: return False

        for i in range(0, len(qty) + 1):
            # split into numeric and unit part
            val = qty[:len(qty)-i]
            unit = qty[len(qty)-i:]

            # handle "?" case (empty value = 1)
            if unit == "?": val = val or "1"

            # check if correct unit is found yet
            if is_num(val):
                # change units to base case
                conversions = { "kg": ("g", 1000), "l":  ("ml", 1000) }
                if unit in conversions:
                    unit, factor = conversions[unit]
                    val = float(val) * factor

                return (float(val), unit)


    def _add_qty(self, target: dict, delta: dict) -> None:
        """Add `delta` item with single qty to `target` item."""
        # split and convert all quantities into value and unit
        d_val, unit = self._split_qty(delta["qtys"])
        t_qtys = [self._split_qty(t_qty) for t_qty in target["qtys"].split(self._seperator)]

        # find index of matching target quantity
        idx = next((i for i, el in enumerate(t_qtys) if el[1].endswith(unit)), -1)

        # update quantity if needed else just append
        if idx != -1:
            t_val = t_qtys[idx][0]
            new_val = float(t_val) + float(d_val)
            t_qtys[idx] = (new_val, unit)

        else: t_qtys.append((d_val, unit))

        # rejoin everything back into single string
        t_qtys = [f"{t_val}{t_unit}" for t_val, t_unit in t_qtys]
        target["qtys"] = self._seperator.join(t_qtys)


    # def _add_qtys(self, target: dict, delta: dict) -> None:
    #     """Add `delta` item with any qtys to `target` item."""
    #     d_qtys = delta["qtys"].split(self._seperator)
    #     for d_qty in d_qtys: 
    #         sub_delta = { "qtys": d_qty }
    #         self._add_qty(target, sub_delta)


    def _add_item(self, item: dict, item_sec: str = "Sonstiges") -> None:
        """Add an `item` to its correct section."""
        # find section the item belongs to
        for section in section_data:
            if item["name"] in section["items"]:
                item_sec = section["name"]; break

        # use generator to find index of item
        items = self._sections[item_sec]
        idx = next((i for i, el in enumerate(items) if el["name"] == item["name"]), -1)

        # if no match found add item as is else update qtys
        if idx == -1: items.append(item)
        else: self._add_qty(target=items[idx], delta=item)


    def add_recipe(self, recipe: dict) -> None:
        """Add `recipie` to list by saving its name and items."""
        # save each scanned recipie as an item like dict
        # in a section with the current date as an overview
        recipie_item = { "name": recipe["name"], "qtys": "1" }
        self._add_item(recipie_item, self._date)
        
        # clean up qtys strings then add each item
        for item in recipe["items"]:
            item["qtys"] = item["qtys"].strip().replace(" ", "")

            # split item into subitems by qtys seperators and
            # then add them one by one to fix qtys like '2kg|500g'
            for qty in item["qtys"].split(self._seperator):
                sub_item = { "name": item["name"], "qtys": qty }
                self._add_item(sub_item)

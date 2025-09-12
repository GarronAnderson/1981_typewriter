import time

import TWComms

tw = TWComms.TWComms()

tw.print("\n===ready===\n")
char = ""
msg = ""
while True:
    tw.print(") ", end="")
    while char != "\n":
        if tw.avaliable():
            char = tw.read()
            msg = msg + char
            print(f"<{char}>")

    if msg == "done\n":
        tw.print("\n===bye===\n\n\n\n\n\n")
        break

    tw.print()
    tw.print(f"Got: {msg}")
    msg = ""
    char = ""

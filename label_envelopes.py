from time import sleep

import TWComms

return_addr = """
The Andersons
1922 124th Street
Lubbock, TX
         79423"""

T = TWComms.TWComms()

done = False

while not done:
    cmd = input("> ")
    if cmd.lower().startswith("q"):
        done = True
    else:
        T.print(return_addr)
        T.return_paper(num_returns=20)

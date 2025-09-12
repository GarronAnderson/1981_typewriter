# pipe test

import TWComms

T = TWComms.TWComms()

import sys
while True:
    line = sys.stdin.readline()
    T.print(line, sep='', end='')
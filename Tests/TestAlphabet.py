from time import sleep, time

import TWComms

T = TWComms.TWComms()
input("Ready")
start = time()
T.print("abcdefghijklmnopqrstuvwxyz")
T.print("abcdefghijklmnopqrstuvwxyz".upper())
T.print("abcdefghijklmnopqrstuvwxyz")
end = time()
total = end - start
T.print(f"Time taken to print 78 chars: {total:.2f} seconds")
T.print(f"Time per char: {total/78} seconds.")
chars_per_second = 78 / total
chars_per_min = chars_per_second * 60
T.print(f"WPM: {chars_per_min/5:.2f}")

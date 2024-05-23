import TWComms
import time

T = TWComms.TWComms()
message_bannered = open("messageBannered.txt").read() + "\n" * 6
message_nobanner = open("message.txt").read() + "\n" * 3

print("Printing...")

T.print(message_nobanner)

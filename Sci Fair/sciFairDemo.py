import TWComms
import time

T = TWComms.TWComms()
message_bannered = open("messageBannered.txt").read() + "\n" * 6
message_nobanner = open("message.txt").read() + "\n" * 6

done = False

while not done:
    demo = input("Demo? (y/n) ").lower().startswith("y")
    if demo:
        banner = input("Banner? (y/n) ").lower().startswith("y")
        if banner:
            T.print(message_bannered)
        else:
            T.print(message_nobanner)
    else:
        # typing demo
        to_print = input("What should I print? ")
        T.print(to_print)
        T.print("\n" * 6)

    done = input("Done? (y/n) ").lower().startswith("y")

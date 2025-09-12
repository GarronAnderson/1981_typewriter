import ezgmail

import TWComms

ezgmail.init()

T = TWComms.TWComms(log=True)


T.print("Fetching mail...")
unread = ezgmail.unread()

T.print(f"You have {len(unread)} unread messages.")
if len(unread) > 5:
    T.print("Printing top 5 unread messages.")

print_text = T.summarize_email(unread[:5])

T.print(print_text)

T.return_until_readable()

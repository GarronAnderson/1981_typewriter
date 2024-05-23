import TWComms
import codes

T = TWComms.TWComms()

codes_existing = [code[0] for code in list(codes.output_lookup.values())]

codes_all = [str(bin(code))[2:].zfill(7) for code in list(range(0, 127))]

codes_nonexistent = [code for code in codes_all if code not in codes_existing]

print(codes_existing, codes_all, codes_nonexistent)

T.print("You are now entering the realm of the STRANGE CODES!")

for code in codes_nonexistent:
    T.print("Testing: " + code)
    T._send_char(code)
    T.return_paper()

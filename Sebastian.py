import TWComms

T = TWComms.TWComms()

for i in range(127):
	T.print(chr(i),end="")

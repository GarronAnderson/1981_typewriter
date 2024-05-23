import TWComms

T = TWComms.TWComms()

import codes

all_codes = codes.output_lookup.keys()

T.print(' '.join(all_codes))


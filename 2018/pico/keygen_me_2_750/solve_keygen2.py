from z3 import *

def addConstraintBetweenXandY(solver, group, x, y, a, b):
	for i in range(0, len(group)):
		solver.add(Or(And(group[i] >= x, group[i] < y), And(group[i] >= a, group[i] < b)))

# Initialize a 16 integer group and the solver
serial = IntVector('serial', 16)
s = Solver()

# Make sure each character is between 'A' and 'Z'
addConstraintBetweenXandY(s, serial, 0x41-0x37, 0x5b-0x37, 0x30-0x30, 0x3a-0x30)

# 1.
s.add((serial[0] + serial[1]) % 0x24 == 0xe)

# 2.
s.add((serial[2] + serial[3]) % 0x24 == 0x18)

# 3.
s.add((serial[2] - serial[0]) % 0x24 == 0x6)

# 4.
s.add((serial[1] + serial[3] + serial[5]) % 0x24 == 0x4)

# 5.
s.add((serial[2] + serial[4] + serial[6]) % 0x24 == 0xd)

# 6.
s.add((serial[3] + serial[4] + serial[5]) % 0x24 == 0x16)

# 7.
s.add((serial[6] + serial[8] + serial[10]) % 0x24 == 0x1f)

# 8.
s.add((serial[1] + serial[4] + serial[7]) % 0x24 == 0x7)

# 9.
s.add((serial[9] + serial[12] + serial[15]) % 0x24 == 0x14)

# 10.
s.add((serial[13] + serial[14] + serial[15]) % 0x24 == 0xc)

# 11.
s.add((serial[8] + serial[9] + serial[10]) % 0x24 == 0x1b)

# 12.
s.add((serial[7] + serial[12] + serial[13]) % 0x24 == 0x17)

if s.check():
	m = s.model()
	real_serial = ''
	for n in serial:
		num = m[n].as_long()
		if 0 <= num <= 9:
			real_serial += chr(num + 0x30)
		else:
			real_serial += chr(num + 0x37)

	print real_serial

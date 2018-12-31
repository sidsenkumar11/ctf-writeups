class Node():
	def __init__(self, val, left=None, right=None):
		self.left = left
		self.right = right
		self.val = val

nodes = []

# Add vertices
nodes.append(Node(0x47BBFA96)) # 0
nodes.append(Node(0x50171A6E)) # 1
nodes.append(Node(0x23DAF3F1)) # 2
nodes.append(Node(0x634284D3)) # 3
nodes.append(Node(0x344C4EB1)) # 4
nodes.append(Node(0x0C4079EF)) # 5
nodes.append(Node(0x425EBD95)) # 6
nodes.append(Node(0x07ACE749)) # 7
nodes.append(Node(0x237A3A88)) # 8
nodes.append(Node(0x4B846CB6)) # 9
nodes.append(Node(0x1FBA9A98)) # 10
nodes.append(Node(0x3A4AD3FF)) # 11
nodes.append(Node(0x16848C16)) # 12
nodes.append(Node(0x499EE4CE)) # 13
nodes.append(Node(0x261AF8FB)) # 14
nodes.append(Node(0x770EA82A)) # 15

vals = {}
vals[str(0x47BBFA96)] = 0
vals[str(0x50171A6E)] = 1
vals[str(0x23DAF3F1)] = 2
vals[str(0x634284D3)] = 3
vals[str(0x344C4EB1)] = 4
vals[str(0x0C4079EF)] = 5
vals[str(0x425EBD95)] = 6
vals[str(0x07ACE749)] = 7
vals[str(0x237A3A88)] = 8
vals[str(0x4B846CB6)] = 9
vals[str(0x1FBA9A98)] = 10
vals[str(0x3A4AD3FF)] = 11
vals[str(0x16848C16)] = 12
vals[str(0x499EE4CE)] = 13
vals[str(0x261AF8FB)] = 14
vals[str(0x770EA82A)] = 15

# Add edges
nodes[0].left = nodes[5]
nodes[0].right = nodes[2]

nodes[1].left = nodes[15]
nodes[1].right = nodes[7]

nodes[2].left = nodes[10]
nodes[2].right = nodes[6]

nodes[3].left = nodes[5]
nodes[3].right = nodes[8]

nodes[4].left = nodes[12]
nodes[4].right = nodes[13]

nodes[5].left = nodes[9]
nodes[5].right = nodes[15]

nodes[6].left = nodes[2]
nodes[6].right = nodes[3]

nodes[7].left = nodes[9]
nodes[7].right = nodes[6]

nodes[8].left = nodes[11]
nodes[8].right = nodes[3]

nodes[9].left = nodes[12]
nodes[9].right = nodes[3]

nodes[10].left = nodes[15]
nodes[10].right = nodes[8]

nodes[11].left = nodes[5]
nodes[11].right = nodes[8]

nodes[12].left = nodes[3]
nodes[12].right = nodes[2]

nodes[13].left = nodes[4]
nodes[13].right = nodes[7]

nodes[14].left = nodes[8]
nodes[14].right = nodes[3]

nodes[15].left = nodes[9]
nodes[15].right = nodes[13]

# Construct path to desired value
# Ignoring cycles in graph for now..

desired = 0x40475194
visited = []

cur = nodes[0]
visited.append(cur)
while cur != desired:
	# print [vals[str(x.val)] for x in visited]
	if cur.left not in visited:
		visited.append(cur.left)
		cur = cur.left
	elif cur.right not in visited:
		visited.append(cur.right)
		cur = cur.right
	else:

		# Pop until we find a right-subtree to visit
		found = False
		visited.pop()
		while not found and visited:
			parent = visited.pop()

			if cur == parent.left and parent.right not in visited:
				visited.append(parent)
				visited.append(parent.right)
				cur = parent.right
				found = True
			else:
				cur = parent

		if not found:
			print "No such combination!"
			import sys
			sys.exit(1)

	# Check if desired value reached
	result = 0
	for node in visited:
		result ^= node.val
	if result == desired:
		break

print "------------------"
print "Solution Found!"
print "------------------"
print [vals[str(x.val)] for x in visited]
print [hex(x.val) for x in visited]

# -*-coding:Utf-8 -*

import os

#-------------------------------------------------------------------------------
class RppNode:

	def __init__(self, name=""):
		self.name = name
		self.children = None
		self.parent = None
		self.values = None

	def create_child(self, name=""):
		child = RppNode(name)
		if self.children == None:
			self.children = [child]
		else:
			self.children.append(child)
		child.parent = self
		return child


#-------------------------------------------------------------------------------
def parse_rpp_file(filePath):
	with open(filePath, 'r') as f:
		root = RppNode()
		node = root

		for line in f:

			line = line.strip()
			if len(line) == 0:
				continue

			if(line[0] == '>'):
				node = node.parent
				continue

			parts = line.split(' ')

			if(line[0] == '<'):
				node = node.create_child(parts[0][1:])
				node.values = parts[1:]
				# Note: initialization required to hint it's an object node
				node.children = []
			else:
				if(len(parts) == 1):
					rawNode = node.create_child("")
					rawNode.values = [parts[0]]
				else:
					p = node.create_child(parts[0])
					p.values = parts[1:]

			#print(line)

	# Return REAPER_PROJECT node (the only one and first in the document)
	return root.children[0]


#-------------------------------------------------------------------------------
def write_rpp_file(filePath, rootNode):
	node = rootNode
	with open(filePath, "w") as f:
		write_rpp_node(f, node, "")

#-------------------------------------------------------------------------------
def write_rpp_node(f, node, indent):
	f.write("{0}<{1}".format(indent, node.name))

	write_rpp_node_values(f, node)
	indent += "  "

	if node.children:
		for child in node.children:
			# Note: compare with None is intentional
			if child.children != None:
				write_rpp_node(f, child, indent)
			else:
				f.write(indent + child.name)
				write_rpp_node_values(f, child)

	indent = indent[:-2]
	f.write("{0}>\n".format(indent))

#-------------------------------------------------------------------------------
def write_rpp_node_values(f, node):
	if node.values:
		for v in node.values:
			f.write(" " + str(v))
	f.write('\n')

#-------------------------------------------------------------------------------
def test():
	# fileName = "Milhana_ep5_scene5_t02.RPP"
	fileName = "empty.RPP"
	dirPath = os.path.join("TestData", "Reaper")
	root = parse_rpp_file(os.path.join(dirPath, fileName))
	write_rpp_file(os.path.join(dirPath, "exportTest.RPP"), root)


#-------------------------------------------------------------------------------
if __name__ == "__main__":
	test()


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

	def get_nodes_by_tag(self, name):
		nodes = []
		for n in self.children:
			if n.name == name:
				nodes.append(n)
		return nodes

	def get_node_by_tag(self, name):
		for n in self.children:
			if n.name == name:
				return n
		return None

#-------------------------------------------------------------------------------
def parse_rpp_file(filePath):
	with open(filePath, 'r') as f:
		root = RppNode()
		node = root

		for line in f:

			line = line.strip()
			if len(line) == 0:
				continue

			if line[0] == '>':
				node = node.parent
				continue

			# Separate first characters from the next argument list
			parts = line.split(' ', 1)
			argList = parts[1] if len(parts)==2 else ""

			if line[0] == '<':
				node = node.create_child(parts[0][1:])

				node.values = parse_values(argList)
				# Note: initialization required to hint it's an object node
				node.children = []
			else:
				if len(parts) == 1:
					rawNode = node.create_child("")
					rawNode.values = [parts[0]]
				else:
					p = node.create_child(parts[0])
					p.values = parse_values(argList)

	# Return REAPER_PROJECT node (the only one and first in the document)
	return root.children[0]

#-------------------------------------------------------------------------------
def parse_values(s, customConvertFunction=None):
	values = []
	s = s.strip()

	i = 0
	while i < len(s):

		if s[i] == ' ':
			i += 1

		elif s[i] == '"':
			i += 1
			buf = ""
			while i < len(s):
				if s[i] != '"':
					buf += s[i]
					i += 1
				else:
					values.append(buf)
					i += 1
					break

		else:
			buf = ""
			while i < len(s) and s[i] != ' ':
				buf += s[i]
				i += 1
			v = ""
			try:
				v = int(buf)
			except ValueError:
				try:
					v = float(buf)
				except ValueError:
					if customConvertFunction:
						v = customConvertFunction(buf)
					else:
						v = buf
			values.append(v)
			i += 1

	return values

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
def is_parsable_as_number(s):
	try:
		float(s)
	except ValueError:
		return False
	return True

#-------------------------------------------------------------------------------
def write_rpp_node_values(f, node):
	if node.values:
		formattedValues = []
		for v in node.values:
			if type(v) == str:
				if len(v) == 0 or v.find(' ') != -1 or is_parsable_as_number(v):
					formattedValues.append('\"' + v + '"')
				else:
					formattedValues.append(v)
			else:
				formattedValues.append(str(v))
		if len(node.name) != 0:
			f.write(' ')
		f.write(' '.join(formattedValues))
	f.write('\n')



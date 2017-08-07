# -*-coding:Utf-8 -*
# ------------------------------------------------------------------------------
# Saga toolkit entry point file
# Author: Marc Gilleron (aka Zylann)
# ------------------------------------------------------------------------------

import sys
import os
import re
# For HTML escaping
import cgi

# ------------------------------------------------------------------------------
class Actor:

	def __init__(self, name="", pseudo=""):
		self.name = name
		self.pseudo = pseudo


# ------------------------------------------------------------------------------
# \brief Top element of an audio production.
class Saga:

	def __init__(self):
		self.title = ""
		self.episodes = []
		self.characters = {}
		self.character_aliases = {}
		self.actors = []

	def create_episode(self):
		episode = Episode(self)
		self.episodes.append(episode)
		return episode

	def get_character(self, name_or_alias):
		name = name_or_alias
		try:
			name = self.character_aliases[name_or_alias]
		except KeyError:
			pass
		return self.characters[name]


# ------------------------------------------------------------------------------
class Episode:

	def __init__(self, saga=None):
		self.saga = saga

		self.title = ""

		# List of all scenes in the episode.
		# It can be empty, depending on how deep STK is told to go through.
		# (It's also related to the parsing format)
		self.scenes = []

		# Name of the file this episode was taken from (without extension)
		self.filename = ""

		self.filetype = "txt"
		self.number = 0

		# Scene indexes at which a part starts (used for big, split episodes).
		self.part_indexes = [0]

	def create_scene(self):
		scene = Scene(self)
		self.scenes.append(scene)
		return scene


# ------------------------------------------------------------------------------
# \brief a scene is the element that contains the actual action, statements etc.
# any parent element (such as the episode) could be dynamic in the future.
class Scene:

	def __init__(self, episode=None):
		self.title = ""
		self.episode = episode
		self.elements = []

	def create_element(self):
		e = SceneElement(self)
		self.elements.append(e)
		return e

	def create_statement(self):
		s = Statement(self)
		self.elements.append(s)
		return s

# ------------------------------------------------------------------------------
class SceneElement:

	def __init__(self, scene=None):
		self.text = ""
		self.scene = scene


# ------------------------------------------------------------------------------
class Statement(SceneElement):

	def __init__(self, scene=None):
		super().__init__(scene)
		# Who speaks (can be an alias)
		self.character_name = ""
		# Note about mood, intonation etc
		self.note = ""
		# Optional flag indicating wether this statement has already been
		# recorded by the actor or not
		self.recorded_by_actor = False
		# Actual text
		self.text = ""

	def get_character(self):
		return self.scene.episode.saga.get_character(self.character_name)


# ------------------------------------------------------------------------------
class Character:

	def __init__(self, saga=None):
		self.name = ""
		# Gender can be M, F or N
		self.gender = "N"
		self.saga = saga
		# Main actor name
		self.actor_name = ""


# ------------------------------------------------------------------------------
class HtmlExporter:

	def __init__(self):
		# Templates
		self.statement_template = ""
		self.root_template = ""
		self.standalone_note_template = ""
		self.scenelist_template = ""

	def load_templates(self, template_folder_path):
		self.statement_template = read_all_file(os.path.join(template_folder_path, "statement.html"))
		self.root_template = read_all_file(os.path.join(template_folder_path, "root.html"))
		self.standalone_note_template = read_all_file(os.path.join(template_folder_path, "standalone_note.html"))
		self.scenelist_template = read_all_file(os.path.join(template_folder_path, "scenelist.html"))

	def export(self, saga, destination_folder_path):
		self.load_templates(os.path.join("templates", "Default"))

		print("Exporting saga...")

		for episode in saga.episodes:
			self.export_episode(episode, destination_folder_path)

		print("Done.")

	def export_episode(self, episode, destination_folder_path):
		content = ""

		# TODO write a better, optimized template system (more like Django?)

		content += self._generate_table_of_contents(episode)

		scene_index = 0

		for scene in episode.scenes:

			scene_title = scene.title or "Untitled scene"
			scene_id = self._make_scene_id(scene_index)
			content += "<h2 id=\"{0}\">{1}</h2>\n".format(scene_id, scene_title)

			for e in scene.elements:

				if type(e) == Statement:
					head_note = ""
					if len(e.note) != 0:
						head_note = "<span class=\"note\">, {0}</span>".format(self._html_chars(e.note))

					statement_block = self.statement_template.format(self._html_chars(e.character_name), \
																	 head_note, \
																	 self._html_chars(e.text))
					content += statement_block;

				else:
					formatted = self.standalone_note_template.format(self._html_chars(e.text))
					content += formatted

			scene_index += 1

		title = episode.title or "Untitled episode"
		full_output = self.root_template.replace("{title}", title).replace("{content}", content)

		dst = os.path.join(destination_folder_path, "{0}.html".format(episode.filename))
		o = open(dst, "w+")
		o.write(full_output)
		o.close()


	def _generate_table_of_contents(self, episode):
		content = "<ul>\n"
		scene_index = 0

		for scene in episode.scenes:
			scene_title = scene.title or "Untitled scene"
			scene_id = self._make_scene_id(scene_index)
			content += '<li><a href="#{0}">{1}</a></li>\n'.format(scene_id, scene_title)
			scene_index += 1

		content += "</ul>\n"

		return self.scenelist_template.replace("{content}", content)

	def _make_scene_id(self, index):
		return "scene" + str(index)

	def _html_chars(self, s):
		# Convert characters so they are HTML-compliant...
		return cgi.escape(s)
		#return s.replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------------------------
# \brief This parser reads files written in a Markdown format that has been
# customized to better respond to the needs of an audio play script.
class MDParser:

	# Note: these regexes are... actually not used^^ I keep them for future reference
	# A note starts with < or ( and ends with > or ).
	regex_standalone_note = re.compile("^\(.*\)$|^<.*>$")
	# A character statement has a double "--" in it, but doesn't starts or end with it.
	regex_statement = re.compile(".+--.+")
	# An h1 is underlined by 3 or more equal symbols, and only that.
	regex_heading1 = re.compile("^==+=$")
	# An h2 is underlined by 3 or more dashes, and only that.
	regex_heading2 = re.compile("^--+-$")

	def __init__(self):
		self.lines = []
		# Current line index
		self.line_index = 0
		# Parsed saga state
		self.saga = None
		self.episode = None
		self.scene = None

	def test():
		print("Match tests:")
		print("Note:")
		c = __class__
		print(c.regex_standalone_note.match("(this is a note)"))
		print(c.regex_standalone_note.match("<this is a note>"))
		print(c.regex_standalone_note.match("(this is not a note"))
		print(c.regex_standalone_note.match("this is not a note)"))
		print(c.regex_standalone_note.match("<this is a weird note)"))


	def parse_file(self, source_file_path):
		print("Parsing file {0}...".format(source_file_path))

		if self.saga == None:
			self.saga = Saga()
			self.episode = self.saga.create_episode()
			self.episode.filename = os.path.splitext(os.path.basename(source_file_path))[0]
			self.scene = self.episode.create_scene()

		# TODO Use `with`
		f = open(source_file_path)
		self.lines = f.readlines()
		f.close()

		self.line_index = 0
		self.parse_lines()

		print("Done")

	def next_line(self):
		self.line_index += 1

	def parse_lines(self):

		while self.line_index < len(self.lines):

			line = self.lines[self.line_index].strip()

			# Print progress
			#progress = math.floor(100.0 * self.line_index / len(self.lines))
			#print("{0}".format(self.line_index))

			if len(line) == 0:
				self.next_line()
				continue

			if line.startswith("/*"):
				self.parse_comment()
				continue

			# Look-ahead parsing
			if self.line_index + 1 < len(self.lines):

				next_line = self.lines[self.line_index + 1].strip()

				# Header 1
				if next_line.startswith("==="):

					if len(self.saga.title) == 0:
						print("Saga title is:", line)
						self.saga.title = line

					if len(self.episode.title) == 0:
						self.episode.title = line

					self.next_line()
					self.next_line()
					continue

				# Header 2
				elif next_line.startswith("---"):

					# if len(self.episode.title) == 0:
					# 	self.episode.title = line

					if len(self.scene.title) == 0:
						self.scene.title = line

					else:
						self.scene = self.episode.create_scene()
						self.scene.title = line

					self.next_line()
					self.next_line()
					continue

			# Note
			if line[0] == '(' or line[0] == '<' or line[0] == '[':
				self.parse_standalone_note()
				continue

			# Statement
			if line.find("--") > 0:
				self.parse_statement()
				continue

			self.next_line()


	def parse_standalone_note(self):
		while self.line_index < len(self.lines):
			line = self.lines[self.line_index].strip()
			self.next_line()

			elem = self.scene.create_element()
			elem.text = line
			#TODO better strip the note

			if len(line) == 0 or line.find(")") or line.find(">") or line.find("]") != -1:
				return

	def parse_statement(self):
		statement = self.scene.create_statement()

		# A statement is a series of lines until the next blank line or other element
		line = self.lines[self.line_index]
		self.next_line()

		char_name = ""
		char_head_note = ""
		statement_text = ""

		statement_head, statement_text = line.split("--", 1)

		# Parse charHead
		comma_index = statement_head.find(",")
		if comma_index != -1:
			char_name, char_head_note = statement_head[0:comma_index], statement_head[comma_index+1:]
		else:
			char_name = statement_head.strip()

		while self.line_index < len(self.lines):
			line = self.lines[self.line_index].strip()
			if len(line) == 0 or line.find("--") > 0:
				break
			else:
				statement_text += line
				self.next_line()

		statement.character_name = char_name
		statement.note = char_head_note
		statement.text = statement_text


	def parse_comment(self):
		while self.line_index < len(self.lines):
			line = self.lines[self.line_index].strip()
			self.next_line()
			if line.startswith("*/") or line.endswith("*/"):
				return


# ------------------------------------------------------------------------------
# Tests if a file can be assumed to contain the script for one episode 
def is_episode_filename(filename):
	filename = filename.lower()
	return filename.contains("episode")


# ------------------------------------------------------------------------------
def print_usage():
	print("Usage: \n")
	print("stk.py <sourceFile> <destinationFolder>")


# ------------------------------------------------------------------------------
def read_all_file(src):
	with open(src, 'r') as content_file:
		content = content_file.read()
	return content


# ------------------------------------------------------------------------------
def cli_main():
	if sys.version_info[0] < 3:
		print("STK needs Python 3.x to run. Check your execution path and file associations.")
		print("Your Python version is: ")
		print(sys.version)
		return

	if len(sys.argv) >= 2:
		if sys.argv[1] == "--test":
			import test
			test.test(sys.argv[2:])

		elif sys.argv[1] == "--markdown2html" and len(sys.argv) == 4:

			input_file = sys.argv[2]
			output_dir = sys.argv[3]

			parser = MDParser()
			parser.parse_file(input_file)

			exporter = HtmlExporter()
			exporter.export(parser.saga, output_dir)

		elif sys.argv[1] == "--generate_ep_card" and len(sys.argv) == 4:
			#generate_episode_card(sys.argv[2], sys.argv[3])
			#TODO generate_episode_card
			print("Not implemented yet...")

		else:
			print_usage()
	else:
		print_usage()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
	cli_main()



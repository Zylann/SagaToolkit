# -*-coding:Utf-8 -*
# ------------------------------------------------------------------------------
# Saga toolkit entry point file
# Author: Marc Gilleron <marc.gilleron@gmail.com>
# ------------------------------------------------------------------------------

import sys
import os


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
		self.characterAliases = {}
		self.actors = []

	def create_episode(self):
		episode = Episode(self)
		self.episodes.append(episode)
		return episode

	def get_character(nameOrAlias):
		name = nameOrAlias
		try:
			name = self.characterAliases[nameOrAlias]
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
		self.partIndexes = [0]

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
		self.characterName = ""
		self.note = ""
		# Optional flag indicating wether this statement has already been
		# recorded by the actor or not
		self.checked = False

	def get_character():
		return self.scene.episode.saga.get_character(self.characterName)


# ------------------------------------------------------------------------------
class Character:

	def __init__(self, saga=None):
		self.name = ""
		# Gender can be M, F or N
		self.gender = "N"
		self.saga = saga
		# Main actor name
		self.actorName = ""


# ------------------------------------------------------------------------------
class HtmlExporter:

	def __init__(self):
		# Templates
		self.statementTemplate = ""
		self.rootTemplate = ""
		self.standaloneNoteTemplate = ""

	def load_templates(self, templateFolderPath):
		self.statementTemplate = read_all_file(os.path.join(templateFolderPath, "statement.html"))
		self.rootTemplate = read_all_file(os.path.join(templateFolderPath, "root.html"))
		self.standaloneNoteTemplate = read_all_file(os.path.join(templateFolderPath, "standalone_note.html"))

	def export(self, saga, destinationFolderPath):
		self.load_templates(os.path.join("Templates", "Default"))

		print("Exporting saga...")

		for episode in saga.episodes:
			self.export_episode(episode, destinationFolderPath)

		print("Done.")

	def export_episode(self, episode, destinationFolderPath):
		content = ""

		# TODO write a better, optimized template system (more like Django?)

		for scene in episode.scenes:

			sceneTitle = scene.title or "Untitled scene"
			content += "<h2>{0}</h2>\n".format(sceneTitle)

			for e in scene.elements:

				if type(e).__name__ == "Statement":
					headNote = ""
					if len(e.note) != 0:
						headNote = "<span class=\"note\"> {0}</span>".format(e.note);

					statementBlock = self.statementTemplate.format(e.characterName, headNote, e.text)
					content += statementBlock;

				else:
					content += self.standaloneNoteTemplate.format(e.note)

		title = episode.title or "Untitled episode"
		fullOutput = self.rootTemplate.replace("{title}", title).replace("{content}", content)

		dst = os.path.join(destinationFolderPath, "{0}.html".format(episode.filename))
		o = open(dst, "w+")
		o.write(fullOutput)
		o.close()


# ------------------------------------------------------------------------------
# \brief This parser reads files written in a Markdown format that has been
# customized to better respond to the needs of an audio play script.
class MDParser:

	def __init__(self):
		self.lines = []
		# Current line index
		self.i = 0
		# Parsed saga state
		self.saga = None
		self.episode = None
		self.scene = None

	def parse_file(self, sourceFilePath):
		print("Parsing file {0}...".format(sourceFilePath))

		if self.saga == None:
			self.saga = Saga()
			self.episode = self.saga.create_episode()
			self.episode.filename = os.path.splitext(os.path.basename(sourceFilePath))[0]
			self.scene = self.episode.create_scene()

		f = open(sourceFilePath)
		self.lines = f.readlines()
		f.close()

		self.i = 0
		self.parse_lines()

		print("Done")

	def next_line(self):
		self.i += 1

	def parse_lines(self):

		while self.i < len(self.lines):
			line = self.lines[self.i].strip()

			# Print progress
			#progress = math.floor(100.0 * self.i / len(self.lines))
			#print("{0}".format(self.i))

			if len(line) == 0:
				self.next_line()
				continue

			if line.startswith("/*"):
				self.parse_comment()
				continue

			isHeading = False

			if self.i > 0:

				previousLine = self.lines[self.i-1].strip()

				if len(previousLine) != 0:

					if len(self.saga.title) == 0 and line.startswith("==="):
						self.saga.title = previousLine

					elif line.startswith("---"):
						isHeading = True

						if len(self.episode.title) == 0:
							self.episode.title = previousLine

						elif len(self.scene.title) == 0:
							self.scene.title = previousLine

						else:
							self.scene = self.episode.create_scene()
							self.scene.title = previousLine

			if line[0] == '(' or line[0] == '<' or line[0] == '[':
				self.parse_standalone_note()
				continue

			if (not isHeading) and line.find("--") > 0:
				self.parse_statement()
				continue

			self.next_line()


	def parse_standalone_note(self):
		while self.i < len(self.lines):
			line = self.lines[self.i].strip()
			self.next_line()

			elem = self.scene.create_element()
			elem.note = line
			#TODO better strip the note

			if len(line) == 0 or line.find(")") or line.find(">") or line.find("]") != -1:
				return

	def parse_statement(self):
		statement = self.scene.create_statement()

		# A statement is a series of lines until the next blank line or other element
		line = self.lines[self.i]
		self.next_line()

		charName = ""
		charHeadNote = ""
		statementText = ""

		statementHead, statementText = line.split("--", 1)

		# Parse charHead
		commaIndex = statementHead.find(",")
		if commaIndex != -1:
			charName, charHeadNote = statementHead[0:commaIndex], statementHead[commaIndex+1:]
		else:
			charName = statementHead.strip()

		while self.i < len(self.lines):
			line = self.lines[self.i].strip()
			if len(line) == 0 or line.find("--") > 0:
				break
			else:
				statementText += line
				self.next_line()

		statement.characterName = charName
		statement.note = charHeadNote
		statement.text = statementText


	def parse_comment(self):
		while self.i < len(self.lines):
			line = self.lines[self.i].strip()
			self.next_line()
			if line.startswith("*/") or line.endswith("*/"):
				return


# ------------------------------------------------------------------------------
# Tests if a file can be assumed to contain the script for one episode 
def is_episode_filename(filename):
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
		return

	if len(sys.argv) == 3:
		parser = MDParser()
		parser.parse_file(sys.argv[1])
		exporter = HtmlExporter()
		exporter.export(parser.saga, sys.argv[2])

	else:
		print_usage()


# ------------------------------------------------------------------------------

if __name__ == '__main__':
	cli_main()



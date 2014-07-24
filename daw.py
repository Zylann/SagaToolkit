# -*-coding:Utf-8 -*

class DawProject:

	def __init__(self):
		self.filePath = ""
		self.tracks = []

	def create_track():
		t = DawTrack()
		self.tracks.append(t)
		return t


class DawTrack:

	def __init__(self):
		self.name = ""
		self.items = []

	def create_item():
		i = DawTrackItem()
		self.items.append(i)
		return i


class DawTrackItem:

	def __init__(self):
		self.sourceFile = ""
		self.name = ""
		self.position = 0
		self.length = 0


class UnsupportedFormat(Exception):

	def __init__(self, filePath):
		self.filePath = filePath
		super().__init__(self, "Unsupported file format " + filePath)


def open_daw_file(filePath):
	fileName, ext = os.path.splitext(filePath)
	ext = ext.lower()
	if ext == "rpp":
		return open_rpp_daw_file(filePath)
	else:
		raise UnsupportedFormat(filePath)


def open_rpp_daw_file(filePath):
	RppNode rpp = parse_rpp_file(filePath)

	project = DawProject
	project.filePath = filePath

	rppTracks = rpp.get_nodes_by_tag("TRACK")

	for rppTrack in rppTracks:

		track = project.create_track()
		track.name = rppTrack.get_node_by_tag("NAME").values[0]

		rppItems = rppTracks.get_nodes_by_tag("ITEM")

		for rppItem in rppItems:

			item = track.create_item()

			item.name = rppItem.get_node_by_tag("NAME").values[0]
			item.position = rppItem.get_node_by_tag("POSITION").values[0]
			item.length = rppItem.get_node_by_tag("LENGTH").values[0]

			source = rppItem.get_node_by_tag("SOURCE")
			if source:
				sourceFile = source.get_node_by_tag("FILE")
				if sourceFile:
					item.sourceFile = sourceFile

	return project


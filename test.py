# -*-coding:Utf-8 -*

import os
import rpp_file
import daw


def test_rpp_file():
	# fileName = "Milhana_ep5_scene5_t02.RPP"
	fileName = "empty.RPP"
	dirPath = os.path.join("TestData", "Reaper")
	root = parse_rpp_file(os.path.join(dirPath, fileName))
	write_rpp_file(os.path.join(dirPath, "exportTest.RPP"), root)


def test_daw():
	project = daw.open_project(os.path.join("TestData", "Reaper", "Milhana_ep5_scene5_t02.RPP"))
	for track in project.tracks:
		for item in track.items:
			print(item.sourceFile)


def test(argv):
	test_daw()



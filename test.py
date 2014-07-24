# -*-coding:Utf-8 -*

import os
import rpp_file
import daw


def test_rpp_file():
	fileName = "empty.RPP"
	dirPath = os.path.join("TestData", "Reaper")
	print("Read...")
	root = rpp_file.parse_rpp_file(os.path.join(dirPath, fileName))
	print("Write...")
	rpp_file.write_rpp_file(os.path.join(dirPath, "exportTest.RPP"), root)
	print("Done.")


def test_daw():
	project = daw.open_project(os.path.join("TestData", "Reaper", "Milhana_ep5_scene5_t02.RPP"))
	for track in project.tracks:
		for item in track.items:
			print(item.sourceFile)


def test_parse_values():
	print(rpp_file.parse_values("ZXZhdxAA"))
	print(rpp_file.parse_values("1 2.5 3"))
	print(rpp_file.parse_values("1 2 \"3a b\""))


def test(argv):
	test_rpp_file()
	#test_parse_values()



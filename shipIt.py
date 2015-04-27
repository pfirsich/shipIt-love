""" Usage:
python shipIt.py config.cfg
See readme for details
"""

import os
import sys

import platform
import fnmatch
import zipfile
import ConfigParser

""" fileList could either be a list of files that should be added to the archive, or a dictionary with the keys being the files to add and the values the filenames inside the archive. """
""" the archive names do not work with zip-cmd yet!! """
def zipArchive(archive, fileList):
	if "zip-cmd" in options:
		if os.path.isfile(archive): os.unlink(archive)
		cmd = options["zip-cmd"].format(archive, " ".join(fileList))
		print "Executing '" + cmd + "'..."
		os.system(cmd)
	else:
		loveZip = zipfile.ZipFile(archive, "w")
		for file in fileList:
			try:
				loveZip.write(file, fileList[file])
			except TypeError: # because list indices must be int, not str (rather than KeyError)
				loveZip.write(file)
		loveZip.close()

if len(sys.argv) < 2:
	sys.exit("No configuration file given.\nUsage: python shipIt.py config.cfg")

cfg = ConfigParser.ConfigParser()
try:
	with open(sys.argv[1]) as file:
		cfg.readfp(file)
except IOError as e:
	sys.exit("Could not open configuration file: " + e)
except ConfigParser.Error as e:
	sys.exit("Config could not be parsed: " + e)

# default options
options = {
	"autodownload": False,
	"target": [],
	"exclude": [],
	"include": [],
	"verbose": False,
	"name": os.path.splitext(os.path.basename(sys.argv[1]))[0],
	"add-to-archive": [],
	"love-exclude": ["changes.txt", "game.ico", "love.ico", "readme.txt", "love.exe"],
}

print "Beginning build process."
platf = platform.platform()
print "Platform: " + platf
print ""

sections = []
# This is done, so sections that match more (/are more specific) are executed later
for section in cfg.sections():
	if platf.startswith(section):
		sections.append((section, len(section)/len(platf)))

sections = map(lambda x: x[0], sorted(sections, key = lambda x: x[1], reverse = False))
sections = ["Global"] + sections

# Parse sections
splitPaths = lambda sect, opt : cfg.get(sect, opt).split(";")
parseMap = {
	"include": splitPaths,
	"exclude": splitPaths,
	"version": cfg.get,
	"zip-cmd": cfg.get,
	"directory": cfg.get,
	"lovedir": cfg.get,
	"autodownload": cfg.getboolean,
	"pre-build": cfg.get,
	"post-build": cfg.get,
	"target": splitPaths,
	"target-directory": cfg.get,
	"name": cfg.get,
	"verbose": cfg.getboolean,
	"add-to-archive": splitPaths,
	"love-exclude": splitPaths,
	"pre-archive": cfg.get,
}
for section in sections:
	for option in cfg.options(section):
		if option not in parseMap:
			sys.exit("Option '" + option + "' not recognized.")
		else:
			options[option] = parseMap[option](section, option)

if options["verbose"]:
	print "(verbose) Options:"
	for option, value in options.iteritems():
		print option + ": " + str(value)
	print ""

# Start build
if "directory" in options:
	os.chdir(options.get("directory"))

if "pre-build" in options:
	print "Executing pre-build command..."
	os.system(options.get("pre-build"))
	print ""

# Build file list
fileList = []
for root, dirs, files in os.walk("."):
	for file in files:
		path = os.path.join(root, file)
		addToList = True
		for exclude in options["exclude"]:
			if fnmatch.fnmatch(path, os.path.join(".", exclude)):
				addToList = False
		for include in options["include"]:
			if fnmatch.fnmatch(path, os.path.join(".", include)):
				addToList = True

		if addToList: fileList.append(os.path.normpath(path))

if options["verbose"]:
	print "(verbose) File list:"
	for file in fileList:
		print file
	print ""

# build .love file

if "target-directory" not in options:
	sys.exit("Target directory has to be set.")

if not os.path.isdir(options["target-directory"]):
	os.makedirs(options["target-directory"])

tempDir = os.path.join(options["target-directory"], "temp")
if not os.path.isdir(tempDir):
	os.makedirs(tempDir)

lovePath = os.path.join(options["target-directory"], options["name"] + ".love")
print "Building '" + lovePath + "'..."
zipArchive(lovePath, fileList)
print ""

os.chdir(options["target-directory"])

# build other targets
for target in options["target"]:
	print "Building target '" + target + "'..."
	if target.startswith("win"):
		# clean up temp folder first
		for file in os.listdir(tempDir):
			os.unlink(os.path.join(tempDir, file))

		if options.get("version") is None:
			print "The love version to use has to be set. Skipping target '" + target + "'."
			continue
		if options.get("lovedir") is None:
			print "The love directory has to be set. Skipping target '" + target + "'."
			continue
			
		if target.endswith("-noarchive"):
			buildArchive = False
			target = target[:-len("-noarchive")]
		else:
			buildArchive = True

		loveTarget = "-".join(["love", options["version"], target])
		loveTargetDir = os.path.join(options["lovedir"], loveTarget)
		if os.path.isdir(loveTargetDir) and os.path.isfile(os.path.join(loveTargetDir, "love.exe")):
			if buildArchive:
				outFilename = os.path.join(tempDir, options["name"] + "-" + target + ".exe")
			else:
				outFilename = options["name"] + "-" + target + ".exe"
				
			print "Writing '" + outFilename + "'..."
			with open(outFilename, "wb") as fused, open(os.path.join(loveTargetDir, "love.exe"), "rb") as loveExe, open(lovePath, "rb") as loveZip:
				fused.write(loveExe.read())
				fused.write(loveZip.read())

			if options.get("pre-archive") is not None:
				cmd = options["pre-archive"].format(outFilename)
				print "Executing '" + cmd + "'..."
				os.system(cmd)

			if buildArchive:
				print "Compiling archive..."
				archiveFiles = {outFilename: os.path.basename(outFilename)}
				for file in filter(lambda file: file not in options["love-exclude"], os.listdir(loveTargetDir)):
					archiveFiles[os.path.join(loveTargetDir, file)] = file
				for file in options["add-to-archive"]:
					archiveFiles[os.path.join(options["directory"], file)] = os.path.split(file)[-1]

				if options["verbose"]:
					print "(verbose) Archive files:"
					for file in archiveFiles:
						try:
							print file + " to " + archiveFiles[file]
						except TypeError:
							print file
					print ""

				targetArchive = os.path.join(".", options["name"] + "-" + target + ".zip")
				zipArchive(targetArchive, archiveFiles)
		else:
			if options["autodownload"] == False:
				sys.exit("Love binaries for target '" + loveTarget + "' could not be found in '" + loveTargetDir + "'.")
			else:
				#TODO: Implement this! (mkdir if not exist, download, unpack)
				print "Automatic love binary download not yet implemented. Skipping target '" + target + "'."
				continue

for file in os.listdir(tempDir):
	os.unlink(os.path.join(tempDir, file))
os.rmdir(tempDir)

# finish build
if "post-build" in options:
	print "Executing post-build command..."
	os.system(options.get("post-build"))
	print ""

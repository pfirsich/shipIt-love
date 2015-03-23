# shipIt-love
A Python script for easily making distributables of your love 2d game.

## Documentation
I included an example .cfg from the game I'm currently working on, SudoHack (and the matching and very useful changeLoveIcon.exe + Source (attention, bad!)) and I think that reading the source code is a lot shorter and easier to understand than this documentation. Linux and Mac targets are not yet implementd, though I presume that .love files will be sufficient for Linux targets.

The "Global" section of a configuration file will always be parsed. Otherwise sections of a configuration file will be matched against Python's platform.platform() in ascending order of matching characters from the start, so more specific sections will be parsed later. Global is always parsed first, so options can conveniently be overriden.

### Global options
#### exclude
Files matching these strings (separated by ';') are not included in the .love file.
#### include
The opposite of exclude, only exists so excludes can be overriden (for excluded subfolders for example)
#### version (mandatory for win*)
The love version (e.g. 0.9.2) the game should be packed with
#### zip-cmd (not fully implemented yet)
If this is not set the script will use Python's built-in ZipFile module. Otherwise the defined command will be executed with {0} being replaced with the archive name and {1} with a list of files. The reason this is not yet fully implemented is that for the final windows archives it must be possible to specify the filenames inside the archive for every file (if we want to avoid copying a whole lot of stuff)
#### name
This determines the name of the built files. If this is not set it is the name of the configuration file (of course without it's file extension)
#### verbose
If this is true, shipIt will out all current options, all files to be packed into the .love and all files to be packed in to the final archives. Default ist false.
#### add-to-archive
These files (separated by ";" again) will be included in the root of the final archives alongside the built binary, the necessary .dlls, etc.

#### directory
The directory of your project's files (source, assets, etc.). This is the directory most files you specify will be relatively specified to (If not said otherwise). If this not specified the path shipIt is executed in will implicitely be "directory".
#### lovedir (mandatory for win*)
This is where the love binaries can be found. This should be an absolute path or a path relative to "directory"!
Inside it there should be directories for different versions and targets: e.g. love-0.9.2-win64, like here: https://bitbucket.org/rude/love/downloads/, but unpacked.
#### autodownload
If this is set to true, shipIt will not download the respective love binaries, but throw an error if they are not already present. Auto downloading is not yet implemented though. Default will be true.
#### target
Which love binaries to build (separated by ';'). The .love file will always be build. Other options are: win32, win64 and win32, win64, which will only build the .exe without archiving it with all necessary .dlls into an archive. (More following?). Default is none.
#### target-directory (mandatory)
In this directory the .love files and archives for the full binary packages will be placed. Also temporary files will be created in it (in the ./temp-subfolder).
#### love-exclude
This is changes.txt;game.ico;love.ico;readme.txt;love.exe per default and contains the files that will not be included from the love-binary distributions into the archive.

#### pre-build
This command will be executed before anything happens, executed in "directory".
#### pre-archive
This command will be executed when .love (in target-directory) and .exes (in target-directory/temp) are generated and the archive is about to be generated
If you want to programmatically change your .exe's icon, do it here (that's what I use it for). {0} is replaced with the path to the .exe file.
#### post-build
This command will be executed after the build process is done, executed in target-directory

// I really don't like this code. It's definitely not pretty, but I had to fight too long to spend time making it pretty.

#include <iostream>
#include <fstream>
#include <windows.h>
// Made using this: http://www.codeguru.com/cpp/w-p/win32/tutorials/article.php/c12873/Hacking-Icon-Resources.htm

struct IconHeader {
	WORD reserved;
	WORD resourceType; // Hopefully 1 for icon
	WORD imageCount;
};

struct IconDirEntry {
	BYTE width;
	BYTE height;
	BYTE colors;
	BYTE reserved;
	WORD planes;
	WORD bitsPerPixel;
	DWORD imageSize;  // size of data
	DWORD imageOffset; // from start of file
};

#pragma pack(push, 2) // This is necessary for the _ResID struct to be 2 bytes smaller (IconDirEntry is 16 bytes and default is 4 byte alignment)
struct IconDirEntry_ResID {
	BYTE width;
	BYTE height;
	BYTE colors;
	BYTE reserved;
	WORD planes;
	WORD bitsPerPixel;
	DWORD imageSize; 
	WORD resourceID; // THIS IS DIFFERENT - id of the single icon image 
};
#pragma pack(pop)


int main(int argc, char** argv) {
	if(argc < 3) {
		std::cout << "Not enough arguments." << std::endl << "Usage: changeIcon.exe <pathto.ico> <pathtoExe>" << std::endl;
		return 0;
	}
	
	HANDLE icoFile = CreateFile(argv[1], GENERIC_READ, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
	if(icoFile == INVALID_HANDLE_VALUE) {
		std::cout << ".ico file could not be opened." << std::endl;
		return 0;
	}
	
	const int maxIcoFileSize = 1024*1024; // 1MB
	unsigned char* icoBuffer = new unsigned char[maxIcoFileSize];
	DWORD bytesRead;
	if(!ReadFile(icoFile, icoBuffer, maxIcoFileSize, &bytesRead, NULL)) {
		std::cout << "The .ico file could not be read." << std::endl;
		return 0;
	}
	
	HANDLE resource = BeginUpdateResource(argv[2], false);
	if(resource == NULL) {
		std::cout << "The specified .exe is not a PE file, does not exist or can't be opened for writing" << std::endl;
		return 0;
	}
	
	IconHeader* header = (IconHeader*)icoBuffer;
	
	unsigned char* iconGroupBuffer = new unsigned char[header->imageCount*sizeof(IconDirEntry_ResID) + sizeof(IconHeader)];
	unsigned char* iconGroupBufferCursor = iconGroupBuffer;
	memcpy(iconGroupBufferCursor, icoBuffer, sizeof(IconHeader));
	iconGroupBufferCursor += sizeof(IconHeader);
	
	IconDirEntry_ResID tempResDirEntry;
	
	for(int img = 0; img < header->imageCount; ++img) {
		IconDirEntry* dirEntry = (IconDirEntry*)(icoBuffer + sizeof(IconHeader) + img * sizeof(IconDirEntry));
		
		memcpy(&tempResDirEntry, dirEntry, sizeof(IconDirEntry_ResID));
		tempResDirEntry.resourceID = img+1;
		
		memcpy(iconGroupBufferCursor, &tempResDirEntry, sizeof(IconDirEntry_ResID));
		iconGroupBufferCursor += sizeof(IconDirEntry_ResID);
		
		// Can't set arbitrary indices to zero to delete them sadly
		if(!UpdateResource(resource, RT_ICON, MAKEINTRESOURCE(img+1), 1033, icoBuffer + dirEntry->imageOffset, dirEntry->imageSize)) {
			std::cout << "Resource update not successful." << std::endl;
			return 0;
		}
	}

	if(!UpdateResource(resource, RT_GROUP_ICON, MAKEINTRESOURCE(1), 1033, iconGroupBuffer, iconGroupBufferCursor - iconGroupBuffer)) {
		std::cout << "Resource update not successful." << std::endl;
		return 0;
	}

	if(!EndUpdateResource(resource, false)) {
		std::cout << "Resource update could not be written." << std::endl;
		return 0;
	}
	
	std::cout << "Icon changed." << std::endl;
	
	return 1;
}
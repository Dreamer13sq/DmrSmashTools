#ifndef DMR_SLOTSPLITTER_CPP
#define DMR_SLOTSPLITTER_CPP

/*
	slotSplitter.cpp by Dreamer13sq

	Takes files from a "master" directory and creates directories with files split into their respective costumes, 
	all inside a "master_out" folder.
	Creates...
		A default folder with the minimum amount of files needed to run for UltimateModManager 
		An "All" folder with all slots containing necessary c00 files to run in ARCropolis
		cXX single slot folders for use in ARCropolis

	To use:
	Your "master" folder should include the minimum files needed for your mod.
		c00 should have the shared files of all cXX folders AND the non-shared files for c00
		cXX should have the non-shared files for each slot
	Your "master" folder can have an "info.txt" file in it's root with options for splitting the files:
		umm = Create UMM folder when splitting
		n  <Name> = ARCropolis/UMM folder Name (name)
		nn <Name> = Single Slot Folder Name (Uses above by default)
		s  <SlotID, Name> = cXX subtitle
		c  <Number> = Number of costumes (8 by default)
		cc <SlotID> = Reserve specific costume slot ("s" also does this)
		i  <Filename> = Ignore file/path/extension
			If you choose to ignore the skeleton file "model.nusktb", you can view models in StudioSB from the master folder 
			and not to worry about deleting the file later after splitting the master.
			Any names with a leading period "." will ignore all filenames with the extension. 
				Ex: ".nuanmb" will ignore all animation files
		a  <Filename> = Copy file to all slots (Including UMM)
			The model file "model.numdlb" is a good option here.
		# = Comment. Line is ignored
	Folders are created on demand - When a file needs to be copied, it will check and create the folder right before doing so.
	This program does NOT clear any files. It only rewrites if necessary. 
		If files are set to be copied and then removed later, they must be manually removed from the "master_out" folder
	Once the above is setup, either drag the "master" folder to the slotSplitter.exe
	or open slotSplitter.exe and provide a path to the master folder.
		When completed, you should have a "master_out" folder with the files split into several directories.

	Compile with:
	g++ -Wall slotSplitter.cpp -o slotSplitter.exe

	Github Link:
	https://github.com/Dreamer13sq/DmrSmashTools/tree/main/SlotSplitter

	Author Email:
	dreamer13sq@gmail.com

	<dirent.h> help from:
	https://www.tutorialspoint.com/how-can-i-get-the-list-of-files-in-a-directory-using-c-or-cplusplus
*/

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <set>
#include <map>
#include <dirent.h>
#include <windows.h>

/*
	From "master"
		Copy all data from c00 to c01, c02, ... c07 in "master_out"
		Then copy leftover files from c01, ..., c07 to "master_out"
*/

const std::string CSPLIT_NAME = "_csplit";

std::string StringReplace(std::string src_str, 
	std::string target_str, std::string new_str)
{
	size_t pos = src_str.find(target_str);
	if ( pos == std::string::npos )
	{
		return src_str;
	}

	src_str.erase(pos, target_str.length());
	return src_str.insert(pos, new_str);
}

class SlotSplitter
{
	enum
	{
		INFO_NONE, INFO_IGNORE, INFO_ALL
	};

public:
	SlotSplitter(std::string _master_path = "", std::string _modname = "")
	{
		master_path = _master_path;
		modname = _modname;

		ResetData();

		Split();
	}

	~SlotSplitter() {};

	// Reset Data
	void ResetData()
	{
		omitSet.clear();
		allSet.clear();
		subtitleMap.clear();
		slotSet.clear();

		out_path = "";
		out_path_umm = "";
		out_path_arc = "";

		makeUMMFolder = false;

		// Omit info.txt by default
		omitSet.insert("info.txt");
	}
	
	// Generate paths from master_path
	void UpdatePaths()
	{
		int l = master_path.length();

		// Find out_path from directory of master_path
		out_path = master_path;
		for ( int i = l - 2; i >= 0; i-- )
		{
			if ( master_path[i] == '/' || master_path[i] == '\\' )
			{
				out_path = master_path.substr(0, i + 1) + "master_out/";
				break;
			}
		}

		// Form paths
		out_path_umm = out_path + modname + " (UMM)/";
		out_path_arc = out_path + modname + " (ARCropolis)/";
		
		for ( auto it = slotSet.begin(); it != slotSet.end(); it++ ) // For each cXX...
		{
			// Has subtitle. Append to path
			if ( subtitleMap.count(*it) > 0 )
			{
				out_path_single[*it] = out_path + modnamesingle + 
					" c0" + std::to_string(*it) + " " + subtitleMap[*it] + "/";
			}
			// No Subtitle
			else
			{
				out_path_single[*it] = out_path + modnamesingle + " c0" + std::to_string(*it) + "/";
			}
		}
	}

	// Returns extension to filename. "" if does not exist
	std::string FilenameExt(std::string fname)
	{
		int l = fname.length();

		for ( int i = l - 1; i >= 0; i-- )
		{
			if (fname[i] == '.') {return fname.substr(i, l - i);}
			if (fname[i] == '/' || fname[i] == '\\') {return "";}
		}

		return "";
	}

	// Copies file to out directory
	void CopyFileToOut(std::string src_path, std::string dest_path)
	{
		std::ifstream srcfile(src_path, std::ios::binary);
		if (!srcfile.is_open()) {return;}

		std::ofstream destfile(dest_path, std::ios::binary);

		destfile << srcfile.rdbuf();
		destfile.close();
		srcfile.close();

		//std::cout << "+ " << dest_path << "\n";
	}
	
	/*
		All parent directories MUST be created ahead of time!
		Accessing "D:/muffins/chaos/fignewtons" WILL NOT WORK UNLESS
		"D:/muffins/chaos/" EXISTS!
		Which is why this function exists
	*/
	// Creates directory and missing directories if they don't exist already
	bool CreateDirectories(std::string path)
	{
		if (usedpaths.count(path) > 0) {return false;}
		usedpaths.insert(path);

		//std::cout << "> " << path << "\n";
		//return true;

		path += "/";
		int l = path.length();
		std::string subpath;

		bool ret = true;

		for ( int i = 0; i < l; i++ )
		{
			if ( path[i] == '.' ) {break;}

			if ( (path[i] == '/') || (path[i] == '\\') )
			{
				subpath = path.substr(0, i) + '\\';
				CreateDirectory(subpath.c_str(), NULL);
			}
		}

		return ret;
	}

	// Reads data from info.txt file and starts the splitting process
	void Split()
	{
		// Ensure master_path has a slash at the end
		if (
			master_path[master_path.length() - 1] != '\\' &&
			master_path[master_path.length() - 1] != '/'
			)
		{
			master_path += "\\";
		}

		// Read info file if exists
		std::fstream infofile(master_path + "info.txt");

		bool noSlotInfo = true;

		if ( infofile.is_open() )
		{
			printf("Reading info.txt\n");

			ResetData();

			std::string line;

			while ( infofile >> line )
			{
				infofile.ignore(); // Skip Space

				// Comments
				if ( line == "#" ) {std::getline(infofile, line);}

				// Modname
				else if ( line == "n" )
				{
					std::getline(infofile, modname);
					modnamesingle = modname;
				}

				// Singleslot Name
				else if ( line == "nn" ) {std::getline(infofile, modnamesingle);}

				// cXX subtitle
				else if ( line == "s" ) 
				{
					int slotNumber;
					infofile >> slotNumber;
					
					infofile.ignore(); // Skip Space
					std::getline(infofile, line);

					if ( slotNumber >= 0 ) 
					{
						subtitleMap[slotNumber] = line;
						slotSet.insert(slotNumber);
						noSlotInfo = false;
					}
				}

				// Reserve costume slots
				else if ( line == "c" )
				{
					int slotNumber;
					infofile >> slotNumber;
					for ( int i = 0; i < slotNumber; i++ )
					{
						slotSet.insert(slotNumber);
						noSlotInfo = false;
					}
				}

				// Reserve costume slots
				else if ( line == "cc" )
				{
					int slotNumber;
					infofile >> slotNumber;
					slotSet.insert(slotNumber);
					noSlotInfo = false;
				}

				// Omit filename/path
				else if ( line == "i" )
				{
					std::getline(infofile, line);
					omitSet.insert(line);
				}

				// Files forced from c00 to all slots
				else if ( line == "a" )
				{
					std::getline(infofile, line);
					allSet.insert(line);
				}

				// Enable UMM export (UMM looks to be obseleted soon)
				else if ( line == "umm" )
				{
					makeUMMFolder = true;
				}

				// Eat.
				else {std::getline(infofile, line);}
			}

			infofile.close();
		}

		if ( modname == "" ) {modname = "MySmashMod";}

		if ( noSlotInfo )
		{
			for ( int i = 0; i < 8; i++ ) {slotSet.insert(i);}
		}

		printf("Finding path names...\n");
		UpdatePaths();

		std::cout << "Mpath: " << master_path
			<< "\nARCropolis: " << out_path_arc << "\n";
		if (makeUMMFolder) {std::cout<< "UMM: " << out_path_umm << "\n";}
		
		if ( omitSet.size() > 0 )
		{
			std::cout << "Omitting...\n";
			for ( auto it = omitSet.begin(); it != omitSet.end(); ++it )
			{
				std::cout << "- " << *it << "\n";
			}
		}

		if ( subtitleMap.size() > 0 )
		{
			std::cout << "Subtitles...\n";
			for ( auto it = subtitleMap.begin(); it != subtitleMap.end(); ++it )
			{
				std::cout << "- " << it->first << " = " << it->second << "\n";
			}
		}

		printf("Entering recursion...\n");
		usedpaths.clear();
		SplitRec("");
	}

	// Recursive function for iterating through directories
	void SplitRec(std::string currentpath, bool do_csplit = false)
	{
		bool in00Root = false, inCXX = false;
		int pathSlotID = -1;

		if ( currentpath.length() > 3 )
		{
			std::string line = currentpath.substr(currentpath.length() - 4, 3);

			in00Root = line == "c00";
			inCXX = line == "c01" || line == "c02" || line == "c03" || line == "c04"
				|| line == "c05" || line == "c06" || line == "c07";
			inCXX = inCXX && !in00Root;

			// Skip if slot is not to be created
			if ( inCXX )
			{
				pathSlotID = std::stoi(line.substr(1, 2));
				if ( slotSet.count(pathSlotID) == 0 )
				{
					return;
				}
			}
		}

		std::string dirpath = master_path + currentpath, 
			temppath, dirnode, csplitname = "", fname;

		DIR *dr;
		struct dirent *en;
		dr = opendir(dirpath.c_str()); //open all or present directory

		std::vector<std::string> subfilenames, subdirs;

		// Find paths and files. Sorts through ommitted
		if (dr) 
		{
			while ( (en = readdir(dr)) != NULL ) 
			{
				dirnode = en->d_name;

				// Invalid
				if (dirnode[0] == '.') {continue;}

				// csplit folder
				if ( dirnode == CSPLIT_NAME )
				{
					csplitname = dirnode;
					continue;
				}

				// Omit
				if ( omitSet.count(dirnode) > 0 ) {continue;}
				if ( omitSet.count(currentpath + dirnode) > 0 ) {continue;}
				if ( omitSet.count(master_path + currentpath + dirnode) > 0 ) {continue;}

				// File
				if ( dirnode.find(".") != std::string::npos )
				{
					// Omit extension
					int pos = dirnode.find(".");
					if ( omitSet.count( dirnode.substr(pos, dirnode.length() - pos) ) > 0 )
					{
						continue;
					}

					// Omit slot
					if ( keyFolderFlag & KEY_FOLDER::UI )
					{
						if ( slotSet.count(std::stoi(dirnode.substr(pos - 2, 2))) == 0 )
						{
							continue;
						}
					}

					subfilenames.push_back(dirnode);
				}
				// Directory
				else
				{
					// Omit slot
					if ( keyFolderFlag & KEY_FOLDER::FIGHTER_BODY )
					{
						if ( dirnode[0] == 'c' )
						{
							if ( slotSet.count(std::stoi(dirnode.substr(1, 2))) == 0 )
							{
								continue;
							}
						}
					}

					subdirs.push_back(dirnode);
				}
			}

			closedir(dr); //close all directory
		}

		// Split csplit folder
		if ( csplitname != "" )
		{
			SplitRec(currentpath + csplitname + "\\", true);
		}

		// Split files
		if ( do_csplit )
		{
			std::string parentpath = currentpath.substr(0, currentpath.length() - CSPLIT_NAME.length() - 1);
			std::cout << parentpath << "\n";

			bool applyToUMMFolder;

			for ( auto subfile_it = subfilenames.begin(); subfile_it != subfilenames.end(); ++subfile_it )
			{
				fname = *subfile_it;

				// UMM (Minimal Slots)
				if ( makeUMMFolder )
				{
					temppath = out_path_umm + parentpath;
					CreateDirectories(temppath);
					CopyFileToOut(dirpath + fname, temppath + fname);
				}

				// Apply to UMM folder if told to do so in info.txt
				applyToUMMFolder = allSet.count(fname) != 0;

				// Copy data to all cXX folders
				for (auto it = slotSet.begin(); it != slotSet.end(); ++it)
				{
					// ARCropolis (Single Slot)
					temppath = out_path_single[*it] + parentpath + "c" + std::to_string(*it) + "\\";
					CreateDirectories(temppath);
					CopyFileToOut(dirpath + fname, temppath + fname);

					// All (All Slots)
					temppath = out_path_arc + parentpath + "c" + std::to_string(*it) + "\\";
					CreateDirectories(temppath);
					CopyFileToOut(dirpath + fname, temppath + fname);

					if ( applyToUMMFolder && makeUMMFolder )
					{
						// UMM (All Slots)
						temppath = StringReplace(parentpath, "c00", "c0" + std::to_string(*it));
						temppath = out_path_umm + temppath;
						CreateDirectories(temppath);
						CopyFileToOut(dirpath + fname, temppath + fname);
					}
				}

				// Arcropolis (All Slots)
				temppath = out_path_arc + currentpath;
				CreateDirectories(temppath);
				CopyFileToOut(dirpath + fname, temppath + fname);
			}
		}
		// Non csplit files
		else
		{
			for ( auto subfile_it = subfilenames.begin(); subfile_it != subfilenames.end(); ++subfile_it )
			{
				fname = *subfile_it;

				// UMM (Minimal Slots)
				if ( makeUMMFolder )
				{
					temppath = out_path_umm + currentpath;
					CreateDirectories(temppath);
					CopyFileToOut(dirpath + fname, temppath + fname);
				}

				// Single Slots
				for (auto it = slotSet.begin(); it != slotSet.end(); ++it)
				{
					// ARCropolis (Single Slot)
					temppath = out_path_single[*it] + currentpath;
					CreateDirectories(temppath);
					CopyFileToOut(dirpath + fname, temppath + fname);
				}
				
				// Arcropolis (All Slots)
				temppath = out_path_arc + currentpath;
				CreateDirectories(temppath);
				CopyFileToOut(dirpath + fname, temppath + fname);
			}
		}

		// Iterate through dirs and set key folder flags
		int popflag = 0;
		for ( auto it = subdirs.begin(); it != subdirs.end(); it++ )
		{
			fname = *it;

			if (keyFolderFlag == 0)
			{
				if ( fname == "effect" )
				{
					popflag |= KEY_FOLDER::EFFECT;
					printf("Entering effect folder...\n");
				}
				else if ( fname == "fighter" )
				{
					popflag |= KEY_FOLDER::FIGHTER;
					printf("Entering fighter folder...\n");
				}
				else if ( fname == "sound" )
				{
					popflag |= KEY_FOLDER::SOUND;
					printf("Entering sound folder...\n");
				}
				else if ( fname == "ui" )
				{
					popflag |= KEY_FOLDER::UI;
					printf("Entering ui folder...\n");
				}
			}
			else if ( keyFolderFlag == KEY_FOLDER::FIGHTER )
			{
				if ( fname == "body" ) {popflag |= KEY_FOLDER::FIGHTER_BODY;}
			}

			keyFolderFlag |= popflag;

			SplitRec(currentpath + fname + "\\");

			keyFolderFlag &= ~popflag; // Clear recently set key folder flag
		}
	}

private:
	std::string master_path, modname, modnamesingle;
	std::string out_path, out_path_umm, out_path_arc;
	std::map<int, std::string> out_path_single; // Holds subtitles to apply to folders

	std::set<int> slotSet; // Holds indices for slots to copy over to
	std::set<std::string> omitSet; // Holds filenames/paths to omit from copying
	std::set<std::string> allSet; // Holds filenames to force copy from c00 to all UMM cXX folders
	std::map<int, std::string> subtitleMap; // Holds subtitles to apply to folders

	std::set<std::string> usedpaths;

	enum KEY_FOLDER
	{
		EFFECT = 1 << 0,
		FIGHTER = 1 << 1,
		SOUND = 1 << 2,
		UI = 1 << 3,
		FIGHTER_BODY = 1 << 4,
	};
	int keyFolderFlag = 0; // Field to denote location in file structure

	bool makeUMMFolder;
};

int main(int argc, char* argv[])
{
	printf("-----------------------------------------------------\n");

	std::string fname = "", modname = "";

	switch ( argc )
	{
		case(3): modname = argv[2];
		case(2): 
			fname = argv[1];

			SlotSplitter split(fname, modname);
			return 0;
	}

	while ( fname != "0" )
	{
		std::cout << "Enter master directory path to create slots for (0 to exit): ";
		std::getline(std::cin, fname);

		if ( fname == "0" ) {break;}
		else
		{
			if ( fname.find("master") == std::string::npos )
			{
				std::cout << "No \"master\" folder in path\n";
				continue;
			}

			std::cout << "Generating...\n";
			SlotSplitter split(fname, modname);
		}
	}

	return 0;
}

#endif
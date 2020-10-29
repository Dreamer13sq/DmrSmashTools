#ifndef DMR_SORTSMD_CPP
#define DMR_SORTSMD_CPP

/*
	sortSmd.cpp by Dreamer13sq

	Sorts triangle data of .smd files based on keywords in the given order:
		- No keyword (Ex: "Wiz_Hair")
		- "vis" (Ex: "zelda_Eye2_VIS_O_OBJShape")
		- "mouth" (Ex: "zelda_PatternA_Mouth_VIS_O_OBJShape")
		- "blink" (Ex: "zelda_Ouch_Blink_VIS_O_OBJShape")

	To use:
	Drag an .smd file onto sortSmd.exe
	or open sortSmd.exe and provide a path to the .smd file to sort

	Compile with:
	g++ -Wall sortSmd.cpp -o sortSmd.exe

	Github Link:
	https://github.com/Dreamer13sq/DmrSmashTools/tree/main/SortSmd

	Author Email:
	dreamer13sq@gmail.com
*/

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <set>
#include <map>
#include <list>

class SortSmd
{
	typedef std::list<std::string> ty_tridata;

public:
	SortSmd(std::string filename = "")
	{
		Reset();

		if ( filename != "" )
		{
			Sort(filename);
		}
	}

	~SortSmd()
	{
		// Clear tridata
		for ( auto it = tridataMap.begin(); it != tridataMap.end(); ++it )
		{
			delete it->second;
		}
	}

	void Reset()
	{
		preTridata.clear();
		tridataMap.clear();

		keyset.clear();
		keysetVis.clear();
		keysetMouth.clear();
		keysetBlink.clear();
	}

	void WriteTriData(std::string meshname, std::ostream& out_file)
	{
		ty_tridata* tridata = tridataMap[meshname];

		// Write Object Data
		for ( auto jt = tridata->begin(); jt != tridata->end(); ++jt )
		{
			//out_file << meshname.substr(firstbonename.length() - 2) + "\n" + *jt;
			out_file << meshname + "\n" + *jt;
		}
	}

	std::string StringLower(std::string name)
	{
		int l = name.length();
		for ( int i = 0; i < l; i++ )
		{
			if ( name[i] >= 'A' && name[i] <= 'Z' )
			{
				name[i] += 32;
			}
		}

		return name;
	}

	void Sort(std::string filename)
	{
		std::fstream file(filename);

		if ( !file.is_open() )
		{
			std::cout << "Error opening file! \"" << filename << "\"\n";
			return;
		}

		ty_tridata* current_tridata; // Used to insert tridata in loop

		std::string line, line2;

		std::getline(file, line, '\n'); // "version 1"
		preTridata.push_back(line + '\n');

		std::getline(file, line, '\n'); // "nodes"
		preTridata.push_back(line + '\n');

		// Read first bone name
		file >> line;
		line2 = line + " ";
		file >> firstbonename;
		line2 += firstbonename + " ";
		file >> line;
		line2 += line;

		preTridata.push_back(line2);

		// Read until triangles
		while ( !file.eof() )
		{
			std::getline(file, line, '\n');
			preTridata.push_back(line + '\n');
			if (line.find("triangles") != std::string::npos) {break;}
		}

		// Triangle Check
		if ( line.find("triangles") == std::string::npos )
		{
			std::cout << "Error finding triangles! \"" << filename << "\"\n";
			file.close();
			return;
		}

		// Read triangles
		while ( !file.eof() )
		{
			std::getline(file, line, '\n');
			if ( line.find("end") != std::string::npos ) {break;}

			// line is object name
			if ( tridataMap.count(line) == 0 )
			{
				tridataMap[line] = new ty_tridata;

				// Insert into appropriate set
				if ( StringLower(line).find("blink") != std::string::npos ) {keysetBlink.insert(line);}
				else if ( StringLower(line).find("mouth") != std::string::npos ) {keysetMouth.insert(line);}
				else if ( StringLower(line).find("vis") != std::string::npos ) {keysetVis.insert(line);}
				else {keyset.insert(line);}

				std::cout << "New Object: " << line << "\n";
			}

			current_tridata = tridataMap[line];

			// Read vertex data
			line2 = "";
			for ( int i = 0; i < 3; i++ )
			{
				std::getline(file, line, '\n');
				line2 += line + "\n";
			}

			current_tridata->push_back(line2);
		}

		file.close();

		// Sort Keys
		std::ofstream out(filename);

		// Write Pre-Triangle Data
		for ( auto it = preTridata.begin(); it != preTridata.end(); ++it ) {out << *it;}

		// Iterate through map using keyvec keys
		for ( auto it = keyset.begin(); it != keyset.end(); ++it) {WriteTriData(*it, out);}
		for ( auto it = keysetVis.begin(); it != keysetVis.end(); ++it) {WriteTriData(*it, out);}
		for ( auto it = keysetMouth.begin(); it != keysetMouth.end(); ++it) {WriteTriData(*it, out);}
		for ( auto it = keysetBlink.begin(); it != keysetBlink.end(); ++it) {WriteTriData(*it, out);}

		out << "end\n";

		out.close();
	}

private:
	std::list<std::string> preTridata; // Non-Triangle Data
	std::map<std::string, ty_tridata*> tridataMap; // String -> Triangle Data
	std::set<std::string> keyset, keysetVis, keysetMouth, keysetBlink; // Used to iterate through map

	std::string firstbonename = "";
};

int main(int argc, char* argv[])
{
	// Run and close
	if ( argc == 2 )
	{
		SortSmd sortsmd(argv[1]);
		return 0;
	}

	std::string fname = "";

	while ( fname != "0" )
	{
		std::cout << "Enter a file to sort (0 to exit): ";
		std::getline(std::cin, fname);

		if ( fname == "0" )
		{
			break;
		}
		else
		{
			if ( fname[0] == '\"' )
			{
				fname = fname.substr(1, fname.length() - 2);
			}

			SortSmd sortsmd(fname);
		}
	}

	return 0;
}

#endif DMR_SORTSMD_CPP
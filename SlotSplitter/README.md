# SlotSplitter
Takes files from a "master" directory and creates directories with files split into their respective costumes, all inside a "master_out" folder.

Creates...
* A default folder with the minimum amount of files needed to run 
* An "All" folder with all slots containing necessary c00 files to run single slot in ARCropolis
* cXX single slot folders for use in ARCropolis

To use:
* Your "master" folder needs to include the minimum files needed for your mod.
	* c00 should have the shared files of all cXX folders AND the non-shared files for c00
	* cXX should have the non-shared files for each slot
* Your "master" folder can have an "info.txt" file in it's root with options for splitting the files:
	* umm = Create UMM folder when splitting
	* n  \<Name\> = ARCropolis/UMM folder Name
	* nn \<Name\> = Single Slot Folder Name (Uses above by default)
	* s  \<SlotID, Name\> = cXX subtitle
	* c  \<Number\> = Number of costumes (8 by default)
	* cc \<SlotID\> = Reserve specific costume slot ("s" also does this)
	* i  \<Filename\> = Ignore file/path
		* If you choose to ignore the skeleton file "model.nusktb", you can view models in StudioSB from the master folder and not to worry about deleting the file later after splitting the master.
	* a  \<Filename\> = Copy file to all slots (Including UMM)
		* The model file "model.numdlb" is a good option here.
	* \# = Comment. Line is ignored
* Folders are created on demand - When a file needs to be copied, it will check and create the folder right before doing so.
* This program does NOT clear any files. It only rewrites if necessary. 
	If files are set to be copied and then removed later, they must be manually removed from the "master_out" folder
* Once the above is setup, either drag the "master" folder to the slotSplitter.exe
or open slotSplitter.exe and provide a path to the master folder.
	* When completed, you should have a "master_out" folder with the files split into several directories.
* I use the "master" folder as my workspace. The "master_out" folder is for mod releases only.

Github Link:
https://github.com/Dreamer13sq/DmrSmashTools/tree/main/SlotSplitter

Author Email:
dreamer13sq@gmail.com

Example of info.txt:
![info.txt_to_out](/images/slotSplitter_example.jpg)

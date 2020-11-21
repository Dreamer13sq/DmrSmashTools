# DmrSmashTools
Some tools used to make modelling more efficient when using Blender.

## Installation
* In Blender, go to Edit > Preferences > Add-ons > Install... and open the DmrSmashTools.py file
* Alternatively you can go to the Text Editor and open it from there. You would need to run the file manually from here.

## Some Operators
* **Duplicate and Mirror**
  * Duplicates selected vertices and mirrors to other side.
  * Performs Remove Doubles, Flip Normals, and Mirror UV afterwards.

* **Bake Shape Keys**
  * Applies vertex transformations from a mesh's shape key values. Removes shape keys afterwards.

* **Match Vertex**
  * Match positions, normals, or weights of selected objects' vertices to those of active object's vertices. 
  * Vertex match range is adjustable.

* **Correct Right Weights**
  * Syncs right side weights to left side's. 
  * Creates new vertex groups where needed. (If "LegL" exists but "LegR" doesn't, "LegR" will be created.)
  * Mirrors vertex groups with no side equivalent along the x-axis (Ex: "Hip"'s weights will be mirrored)

* **Prime Data for SMD**
  * Renames materials to object names for .smd export.

* and some others
  
Github Link: https://github.com/Dreamer13sq/DmrSmashTools/tree/main/DmrSmashTools_Blender

Email: dreamer13sq@gmail.com

Snapshot of addon:

![DmrSmashTools Addon Snapshot](/images/blenderaddon_snapshot.jpg)

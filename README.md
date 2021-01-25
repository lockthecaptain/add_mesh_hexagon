# add_mesh_hexagon

### Blender Add-on for creating a subdivided, UV mapped hexagon

A little add-on for creating a subdivided hexagon mesh in Blender (2.80 +). 

This script **heavily** relies on [this](http://www.voidinspace.com/2014/07/project-twa-part-1-generating-a-hexagonal-tile-and-its-triangular-grid/) article. I've translated the C# code into Python, added UV coordinate generation and packaged it.

### Usage:
- Subdivisions: number of subdivisions, minimum 1, maximum 200
- Radius: radius of the hexagon
- UV: pre-generating UV coordinates

### Installation:
- After downloading the script it can be installed manually from Blender's preferences -> Add-ons -> Install...

bl_info = {
    "name": "Add a subdivided hexagon mesh",
    "author": "Arpad Telkes (lockthecaptain)",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds a hexagon",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}

import math
import bmesh
import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty, EnumProperty, BoolProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


def create_hex(subdivisions, radius, gen_uvs):
    
    # Some variables we'll need for the calculations
    sin60 = math.sin(math.pi / 3.0)
    inv_tan60 = 1.0 / math.tan(math.pi / 3.0)
    rds = radius / float(subdivisions)
 
    current_num_points  = 0
    prev_row_num_points = 0

    np_col_0 = 2 * subdivisions + 1
    col_min	= -subdivisions
    col_max	= subdivisions
    

    # Creating the arrays that will be holding the mesh data
    vertices = []
    indices = []
    vertices_index = 0
    
    # If UV generation is enabled we'll create that array too
    if (gen_uvs == True):
        uvs = []

    # Now let's generate the grid
    # First we'll iterate through the Columns, starting from the bottom (fA)
    for itc in range(col_min, col_max + 1):

        # Calculate x for this row
	# That's the same for each point in this column
        x = sin60 * rds * float(itc)

        # Calculate how many points (y values) we need to generate on for this column
        np_col_i = np_col_0 - abs(itc)
        
        # [row_min, row_max]
        row_min = -subdivisions
        if itc < 0:
            row_min += abs(itc)

        row_max = row_min + np_col_i - 1
        
        # We need this for the indices
        current_num_points += np_col_i

	# Iterate through the Rows (fB)
        for itr in range(row_min, row_max + 1):
            
            # Calculate y
            y = inv_tan60 * x + rds * float(itr)            
            vertices.append((x, y, 0.0))
            
            # If UV generation is required we do it below
            if (gen_uvs == True):        
                uvx = (x + radius) / (radius * 2.0)
                uvy = (y + radius) / (radius * 2.0)
                uvs.append((uvx, uvy))

            # Indices
	    # From each point we'll try to create triangles left and right
            if (vertices_index < (current_num_points - 1)):
            
                # Triangles left from this column
                if (itc >= col_min and itc < col_max):
                
                    # To get the point above
                    pad_left = 0
                    if (itc < 0):
                        pad_left = 1

                    # Adding indices 
                    a = vertices_index
                    b = vertices_index + 1
                    c = vertices_index + np_col_i + pad_left
                    indices.append((a, b, c))
         
                # Triangles right from this column
                if (itc > col_min and itc <= col_max):
                
                    # To get point below
                    pad_right = 0
                    if (itc > 0):
                        pad_right = 1
 
                    a = vertices_index + 1
                    b = vertices_index
                    c = vertices_index - prev_row_num_points + pad_right
                    indices.append((a,b,c))

            # Next vertex
            vertices_index += 1

        prev_row_num_points = np_col_i
    
    # Create the mesh from the vertices and indices
    mesh = bpy.data.meshes.new(name="Hex")
    mesh.from_pydata(vertices, [], indices)
    mesh.validate()

    # If UV generation is required we add UV coordinate to a bmesh below
    if (gen_uvs == True):  

        bm = bmesh.new()
        bm.from_mesh(mesh)

        # Ensure that there is a layer of UV data.
        uv_verify = bm.loops.layers.uv.verify()

        # Loop through faces.
        bm_faces = bm.faces
        for bm_face in bm_faces:

            bm_idx = bm_face.index
            uv_idx_tup = indices[bm_idx]
          
            # Each face is expected to contain 3 elements.
            loop_idx = 0
            face_loops = bm_face.loops

            for bm_loop in face_loops:
                loop_uv_layer = bm_loop[uv_verify]
                uv_idx = uv_idx_tup[loop_idx]

                # Acquire UV coordinate with UV index,
                # assign to loop's UV layer coordinate.
                loop_uv_layer.uv = uvs[uv_idx]
                loop_idx = loop_idx + 1

        # bmeshback to mesh then freeing bmesh up and returning mesh
        bm.to_mesh(mesh)
        bm.free()
        
    return mesh
    

def add_hex(self, context):

    mesh = create_hex(self.subdivisions, self.radius, self.gen_uvs)
    object_data_add(context, mesh, operator=self)


class OBJECT_OT_add_hex(Operator, AddObjectHelper):
    """Create a new subdivided hexagon"""
    bl_idname = "mesh.add_hex"
    bl_label = "Add hexagon"
    bl_options = {'REGISTER', 'UNDO'}
    
    subdivisions: IntProperty(
        name="Subdivisions",
        description="Subdivisions of hexagon",
        min=1, max=200,
        default=4,
    )
    radius: FloatProperty(
        name="Radius",
        description="Radius of hexagon",
        min=0.01, max=100.0,
        default=1.0,
    )
    
    gen_uvs: BoolProperty(
        name="UV",
        description="Generate UV coordinates",       
        default=True,
    )
    # generic transform props
    align_items = (
        ('WORLD', "World", "Align the new object to the world"),
        ('VIEW', "View", "Align the new object to the view"),
        ('CURSOR', "3D Cursor", "Use the 3D cursor orientation for the new object")
    )
    align: EnumProperty(
        name="Align",
        items=align_items,
        default='WORLD',
        update=AddObjectHelper.align_update_callback,
    )
    location: FloatVectorProperty(
        name="Location",
        subtype='TRANSLATION',
    )
    rotation: FloatVectorProperty(
        name="Rotation",
        subtype='EULER',
    )
    
    def execute(self, context):

        add_hex(self, context)

        return {'FINISHED'}


# Registration

def add_hex_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_hex.bl_idname,
        text="Hexagon",
        icon='MESH_PLANE')


# This allows you to right click on a button and link to documentation
#def add_object_manual_map():
#    url_manual_prefix = "https://docs.blender.org/manual/en/latest/"
#    url_manual_mapping = (
#        ("bpy.ops.mesh.add_object", "scene_layout/object/types.html"),
#    )
#    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(OBJECT_OT_add_hex)
    #bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.append(add_hex_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_hex)
    #bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_hex_button)


if __name__ == "__main__":
    register()

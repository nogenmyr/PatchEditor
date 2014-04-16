# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "PatchEditor",
    "author": "Karl-Johan Nogenmyr",
    "version": (0, 1),
    "blender": (2, 7, 0),
    "api": 35622,
    "location": "Tool Shelf",
    "description": "Enbles detailed editing of patches",
    "warning": "not much tested yet",
    "wiki_url": "",
    "tracker_url": "",
    "support": 'COMMUNITY',
    "category": "OpenFOAM"}

#----------------------------------------------------------
# File scene_props.py
#----------------------------------------------------------
import bpy
import mathutils
from bpy.props import *
 
def pedpatchColor(patch_no):
    color = [(1.0,0.,0.), (0.0,1.,0.),(0.0,0.,1.),(0.707,0.707,0),(0,0.707,0.707),(0.707,0,0.707)]
    return color[patch_no % len(color)]

def initpedProperties():

    bpy.types.Scene.firstBoundrayFace = IntProperty(
        name = "1st BC face", 
        description = "The first boundary face in mesh (see boundary file)",
        min = 0)

    bpy.types.Scene.pedpatchName = StringProperty(
        name = "Name",
        description = "Specify name of patch (max 31 chars)",
        default = "defaultName")
    return


#
#    Menu in UI region
#
class PEUIPanel(bpy.types.Panel):
    bl_label = "PatchEditor settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.active_object
        settings = context.tool_settings
        try:
            obj['PatchEditor']
        except:
            layout.operator("read.pedfile")
        else:
            layout.operator("write.pedfile")
            layout.operator("read.pedfile")
            layout.operator("setup.patches")
            layout.prop(scn, 'firstBoundrayFace')
            
            box = layout.box()
            box.label(text="Patch settings")
            box.prop(scn, 'pedpatchName')
            box.operator("set.pedpatchname")
            for m in obj.data.materials:
                try:
                    textstr = m.name
                    split = box.split(percentage=0.2, align=False)
                    col = split.column()
                    col.prop(m, "diffuse_color", text="")
                    col = split.column()
                    col.operator("set.pedgetpatch", text=textstr, emboss=False).whichPatch = m.name
                except:
                    pass
        
class OBJECT_OT_setupPatches(bpy.types.Operator):
    '''Set up patches'''
    bl_idname = "setup.patches"
    bl_label = "Setup initial patches"

    def execute(self, context):
        obj = context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.wm.context_set_value(data_path="tool_settings.mesh_select_mode", value="(False,False,True)")
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        patch = 0
        for f_id, f in enumerate(obj.data.polygons):
            obj.data.polygons[f_id].select = True
            if (f_id+1) in obj['startFaces']:
                bpy.ops.object.mode_set(mode='EDIT')
                obj.active_material_index = patch
                bpy.ops.object.material_slot_assign()
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                patch += 1
        return {'FINISHED'}


class OBJECT_OT_pedSetPatchName(bpy.types.Operator):
    '''Set the given name to the selected faces'''
    bl_idname = "set.pedpatchname"
    bl_label = "Set Patch"
    
    def execute(self, context):
        scn = context.scene
        obj = context.active_object
        bpy.ops.object.mode_set(mode='OBJECT')
        namestr = scn.pedpatchName
        namestr = namestr.strip()
        namestr = namestr.replace(' ', '_')
        try:
            mat = bpy.data.materials[namestr]
            patchindex = list(obj.data.materials).index(mat)
            obj.active_material_index = patchindex
        except: # add a new patchname (as a blender material, as such face props are conserved during mesh mods)
            mat = bpy.data.materials.new(namestr)
            mat.diffuse_color = pedpatchColor(len(obj.data.materials)-1)
            bpy.ops.object.material_slot_add() 
            obj.material_slots[-1].material = mat
        bpy.ops.object.editmode_toggle()  
        bpy.ops.object.material_slot_assign()
        return {'FINISHED'}

class OBJECT_OT_pedGetPatch(bpy.types.Operator):
    '''Click to select faces belonging to this patch'''
    bl_idname = "set.pedgetpatch"
    bl_label = "Get Patch"
    
    whichPatch = StringProperty()

    def execute(self, context):
        scn = context.scene
        obj = context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.wm.context_set_value(data_path="tool_settings.mesh_select_mode", value="(False,False,True)")
        for f in obj.data.polygons:
            f.select = False
        mat = bpy.data.materials[self.whichPatch]
        patchindex = list(obj.data.materials).index(mat)
        obj.active_material_index = patchindex
        bpy.ops.object.editmode_toggle()  
        bpy.ops.object.material_slot_select()
        scn.pedpatchName = self.whichPatch
        return {'FINISHED'}

class OBJECT_OT_writeped(bpy.types.Operator):
    '''Write output fileds for selected object'''
    bl_idname = "write.pedfile"
    bl_label = "Write"
    
    filepath = StringProperty(
            name="File Path",
            description="Filepath used for exporting the file",
            maxlen=1024,
            subtype='FILE_PATH',
            )

    check_existing = BoolProperty(
            name="Check Existing",
            description="Check and warn on overwriting existing files",
            default=True,
            options={'HIDDEN'},
            )

    def invoke(self, context, event):
        import os
        try:
            path = context.active_object['casepath']
            self.filepath = os.path.join(path,'system','createPatchDict')
        except:
            self.filepath = 'createPatchDict'
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        from io_scene_obj import export_obj
        import os
        scn = context.scene
        obj = context.active_object
        bpy.ops.object.mode_set(mode='OBJECT')

        patchAddr = {}
        for m in obj.data.materials:
            patchAddr[m.name] = []
            patchindex = list(obj.data.materials).index(m)
            for f_id, f in enumerate(obj.data.polygons):
                if f.material_index == patchindex:
                    patchAddr[m.name].append(f_id+scn.firstBoundrayFace)

        path = os.path.dirname(self.filepath)
        pathBatchFile = os.path.join(path,'..','batchFile')
        batch = open(pathBatchFile, 'w')
        Dict = open(self.filepath, 'w')
        Dict.write('''FoamFile\n{\n    version     2.0;\n    format      ascii;
    class       dictionary;\n    object      createPatchDict;\n}\n\npointSync false;\npatches\n(\n''')
        for key, facenr in patchAddr.items():
            batch.write("faceSet {} new labelToFace ({}))".format(key, ' '.join(str(n) for n in facenr)) + "\n")
            Dict.write('''    {{\n        name {0};
        patchInfo\n        {{\n            type wall;\n        }}\n        constructFrom set;
        set {0};\n    }}\n'''.format(key))

        Dict.write(");\n")
        Dict.close()
        batch.close()
        
        return{'FINISHED'}
        
def do_import(context, props, filepath, objname, scale):
    os = bpy.path._os
    patch_names = []
    startFaces = [0]
    verts = []
    faces = []
    objname = "patchEditor"
    in_file = open(filepath, "r")
    for line in in_file:  # .readlines():
        line_split = line.split()

        if not line_split:
            continue

        if "nFaces" in line:
            patch_names.append(line_split[2])
            nFaces = int(line.replace(")", "").split()[-1])
            startFaces.append(startFaces[-1]+nFaces)
            continue
            
                
        line_start = line_split[0]  # we compare with this a _lot_
        if line_start == 'v':
            x = float(line_split[1])
            y = float(line_split[2])
            z = float(line_split[3])
            verts.append( mathutils.Vector((x,y,z)) )
            continue
        if line_start == 'f':
            face_verts = []
            for f_node in line_split[1:]:
                face_verts.append(int(f_node) - 1)
            faces.append(face_verts)
            continue
        if line_start == 'o':
            objname = line_split[1]

    mesh = bpy.data.meshes.new(objname)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(objname, mesh)
    bpy.context.scene.objects.link(obj)
    obj.select = True
    bpy.context.scene.objects.active = obj
    for p_id, patch in enumerate(patch_names):
        mat = bpy.data.materials.new(patch)
        mat.diffuse_color = pedpatchColor(p_id)
        bpy.ops.object.material_slot_add() 
        obj.data.materials.append(mat)
    in_file.close()
    obj = context.active_object
    obj.name = objname
    obj.scale = mathutils.Vector([scale,scale,scale])
    bpy.ops.object.transform_apply(scale=True)
    obj['PatchEditor'] = True
    obj['casepath'] = os.path.dirname(filepath)
    obj['startFaces'] = startFaces
# Cannot do initial setup of patches here... context wrong?!
    return startFaces

###### IMPORT OPERATOR #######
class OBJECT_OT_readped(bpy.types.Operator):
    bl_idname = "read.pedfile"
    bl_label = "Import patches (.obj)"
    filename_ext = ".obj"
    
    filepath = StringProperty(
            name="File Path",
            description="Filepath used for importing the file",
            maxlen=1024,
            subtype='FILE_PATH',
            )

    scaleFloat = FloatProperty(
        name = "scale", 
        description = "Scale to Blender units",
        default = 1.,
        min = 0)
            
    def execute(self, context):
        os = bpy.path._os
        props = self.properties
        filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
        objname = os.path.splitext(os.path.basename(filepath))[0]
        bpy.ops.object.select_all(action='DESELECT')
        do_import(context, props, filepath, objname, self.scaleFloat)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



initpedProperties()  # Initialize 

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)


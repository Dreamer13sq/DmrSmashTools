# DmrSmashTools by Dreamer
# Github Link: https://github.com/Dreamer13sq/DmrSmashTools/tree/main/DmrSmashTools_Blender

bl_info = {
    "name": "Dmr Smash Tools",
    "description": 'Some tools used to make models more efficiently.',
    "author": "Dreamer",
    "version": (1, 0),
    "blender": (2, 90, 0),
    "category": "3D View",
    "warning": 'To have addon operators appear in a search in Blender 2.9, Enable "Developer Extras" in Edit > Preferences > Interface > Display'
}

import bpy

# Utility Functions =====================================================

def lastLetters(name):
    i = len(name)
    char = 0;
    for i in range(1, len(name)):
        char = name[-i];
        if (char >= "0" and char <= "9") or char == ".":
            continue;
        return name[-i:];
    return 0;

# Returns last letter in string
def lastLetter(name):
    for i in range(1, len(name)):
        if name[-i].isalpha():
            return name[-i];
    return 0;

# Changes left name to right and vice-versa ("ShoulderL" -> "ShoulderR")
def switchName(name):
    i = len(name)
    char = 0;
    for i in range(1, len(name)):
        char = name[-i];
        if char.isdigit() or char == ".":
            continue;
        name = list(name)
        if name[-i] == "L":
            name[-i] = "R";
        else:
            name[-i] = "L"; 
        name = "".join(name);
        return name;
    i = len(name)
    char = 0;
    for i in range(1, len(name)):
        char = name[-i];
        if (char >= "0" and char <= "9") or char == ".":
            continue;
        name = list(name)
        if name[-i] == "L":
            name[-i] = "R";
        else:
            name[-i] = "L"; 
        name = "".join(name);
        return name;

# Returns list of vertices in vertex group
def FindVertexGroupVertices(mesh_object, groupname_or_index):
    vert = [];
    
    vertexGroups = mesh_object.vertex_groups;
    targetGroupIndex = None;
    
    # Given a name
    if isinstance(groupname_or_index, str):
        for vgroup in vertexGroups:
            if vgroup.name == groupname_or_index:
                targetGroupIndex = vgroup.index;
                break;
    # Given an index
    elif isinstance(groupname_or_index, int):
        for vgroup in vertexGroups:
            if vgroup.index == groupname_or_index:
                targetGroupIndex = vgroup.index;
                break;
    
    # Find vertices of group
    for v in mesh_object.data.vertices:
        for vge in v.groups:
            if vge.group == targetGroupIndex:
                vert.append(v);
                break;
    
    return vert;

# Returns true if distance between vertices is within given distance
def VertexInDist(v1, v2, dist):
    x = v1.co[0] - v2.co[0];
    y = v1.co[1] - v2.co[1];
    z = v1.co[2] - v2.co[2];
    return (x*x + y*y + z*z) <= dist;

# Returns closest vertex in vertex data. None if none is found under dist
def FindClosestVertex(sourceVertex, other_vertices, dist):
    dist *= dist;
    
    lastdist = dist;
    lastVertex = None;
    
    for v in other_vertices:
        x = v.co[0] - sourceVertex.co[0];
        y = v.co[1] - sourceVertex.co[1];
        z = v.co[2] - sourceVertex.co[2];
        dist = x*x + y*y + z*z;
        
        if dist <= lastdist:
            lastVertex = v;
            lastdist = dist;
            print(dist)
    
    return lastVertex;

# Returns list of closest vertices in vertex data. Empty if none is found under dist
def FindClosestVertices(sourceVertex, other_vertices, dist):
    dist *= dist;
    vertexList = [];
    
    for v in other_vertices:
        x = v.co[0] - sourceVertex.co[0];
        y = v.co[1] - sourceVertex.co[1];
        z = v.co[2] - sourceVertex.co[2];
        
        if (x*x + y*y + z*z) <= dist:
            vertexList.append(v);
    
    return vertexList;

# Clear weights from vertex
def ClearVertexWeights(v, vertexGroups):
    for vge in v.groups:
        vertexGroups[vge.group].remove([v.index]);

# Set Vertex Weight. Creates groups where necessary
def SetVertexWeight(v, weight_value, groupname, vertexGroups):
    # Group exists
    if groupname in vertexGroups.keys():
        vertexGroups[groupname].add([v.index], weight_value, 'REPLACE');
    # Create new group and add
    else:
        vertexGroups.new(name = groupname).add([v.index], weight_value, 'ADD');

# Get object Mode
def GetViewMode():
    return bpy.context.active_object.mode;

# Set object Mode. Returns previously set mode
def SetViewMode(mode):
    previous_mode = bpy.context.active_object.mode;
    bpy.ops.object.mode_set(mode = mode);
    return previous_mode;

# Panels =====================================================

class DmrSmashToolsPanel(bpy.types.Panel): # ------------------------------
    bl_label = "Dmr Smash Tools"
    bl_idname = "DMR_SMASH_PT_MAINPANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Dmr" # Name of sidebar
    #bl_parent_id = 'DmrSmashToolsPanel' # Nested Panels
    
    def draw(self, context):
        layout = self.layout
        # Sub-Layouts: row(), column(), column_flow(), grid_flow(), box(), split(), menu_pie()
        
        section = layout.box()
        #section.emboss = 'NORMAL'
        
        section.label(text = "Vertex", icon = 'VERTEXSEL');
        subsection = section.column();
        subsection.operator('dmr_smash.snap_to_active')
        subsection.operator('dmr_smash.snap_vertices')
        subsection.operator('dmr_smash.match_vertex_inner')
        subsection.operator('dmr_smash.dup_and_mirror')
        subsection.operator('dmr_smash.bake_shape_keys');
        
        section.label(text = 'Object Vertex Match', icon = 'ARROW_LEFTRIGHT');
        subsection = section.row(align = True);
        subsection.operator('dmr_smash.match_vertex', text = "Vertex")
        subsection.operator('dmr_smash.match_normals', text = "Normal")
        subsection.operator('dmr_smash.match_weights', text = "Weight")
        
        section = layout.box()
        section.label(text = "Bones", icon = 'BONE_DATA')
        section = section.column();
        section.operator('dmr_smash.toggle_pose')
        section.operator('dmr_smash.clear_pose_transform')
        section.operator('dmr_smash.bone_match_mirror')
        
        section = layout.box()
        sub = section.column()
        sub.label(text = "Weights", icon = 'MOD_VERTEX_WEIGHT')
        sub.operator('dmr_smash.correct_weights', icon = 'SOLO_OFF')
        sub.operator('dmr_smash.toggle_editmode_weights')
        sub.operator('dmr_smash.mirror_selected_weights')
        sub.operator('dmr_smash.weights_to_selected')
        sub = section.column()
        sub.operator('dmr_smash.remove_empty_groups')
        sub.operator('dmr_smash.clear_weights_from_selected')
        sub.operator('dmr_smash.clear_right_groups')
        #sub.operator('dmr_smash.copy_right_groups')
        
        section = layout.box()
        section.label(text = "Etc", icon = 'SOLO_ON')
        section = section.column();
        section.operator('dmr_smash.reset_3dcursor', icon = 'PIVOT_CURSOR')
        section.operator('dmr_smash.image_reload', icon = 'IMAGE_DATA')
        section.operator('dmr_smash.play_anim', icon = 'PLAY')
        section.operator('dmr_smash.clean_materials', icon = 'MATERIAL')
        section.operator('dmr_smash.prime_for_smd', icon = 'FILE_CACHE')

class DmrSmashToolsUVPanel(bpy.types.Panel): # ------------------------------
    bl_label = "Dmr Smash Tools UV"
    bl_idname = "DMR_SMASH_PT_UVPANEL"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Dmr" # Name of sidebar
    
    def draw(self, context):
        layout = self.layout
        
        section = layout.box()
        section.label(text = "UV", icon = 'UV')
        section.operator('dmr_smash.uv_align')
        subsection = section.column()
        #subsection.operator('dmr_smash.face_to_square')
        subsection.operator('dmr_smash.follow_active_quads')
        
        section = layout.box()
        section.label(text = "Etc", icon = 'SOLO_OFF')
        section.operator('dmr_smash.image_reload', icon = 'IMAGE_DATA')
   
# Operators =====================================================

class DMR_SMASH_SNAPSELECTIONTOACTIVE(bpy.types.Operator): # ------------------------------
    bl_label = "Snap Selection To Active"
    bl_idname = 'dmr_smash.snap_to_active'
    bl_description = 'Moves Selected Vertices to Active Element';
    
    def execute(self, context):
        bpy.ops.view3d.snap_selected_to_active();
        return {'FINISHED'}

class DMR_SMASH_PLAYANIM(bpy.types.Operator): # ------------------------------
    bl_label = "Play/Pause Animation"
    bl_idname = 'dmr_smash.play_anim'
    bl_description = 'Toggles animation playback';
    
    def execute(self, context):
        bpy.ops.screen.animation_play();
        return {'FINISHED'}

class DMR_SMASH_TOGGLEPOSE(bpy.types.Operator): # ------------------------------
    bl_label = "Toggle Pose Mode"
    bl_idname = 'dmr_smash.toggle_pose'
    bl_description = 'Toggles Pose Mode for all armatures';
    
    def execute(self, context):
        for o in context.scene.objects:
            if o.type == 'ARMATURE':
                armature = o.data;
                if armature.pose_position == 'REST':
                    armature.pose_position = 'POSE';
                else:
                    armature.pose_position = 'REST'
        return {'FINISHED'}

class DMR_SMASH_EDITMODEWEIGHTS(bpy.types.Operator): # ------------------------------
    bl_label = "Toggle Edit Mode Weights"
    bl_idname = 'dmr_smash.toggle_editmode_weights'
    bl_description = 'Toggles Weight Display for Edit Mode';
    
    def execute(self, context):
        bpy.context.space_data.overlay.show_weight = not bpy.context.space_data.overlay.show_weight;
        
        return {'FINISHED'}

class DMR_SMASH_IMGRELOAD(bpy.types.Operator): # ------------------------------
    bl_label = "Reload All Images"
    bl_idname = 'dmr_smash.image_reload'
    bl_description = 'Reloads all images from files';
    
    def execute(self, context):
        for image in bpy.data.images:
            image.reload()
        
        return {'FINISHED'}

class DMR_SMASH_FOLLOWQUADS(bpy.types.Operator): # ------------------------------
    bl_label = "Follow Active Quads";
    bl_idname = 'dmr_smash.follow_active_quads';
    bl_description = 'Runs "Follow Active Quads" on face';
    
    def execute(self, context):
        bpy.ops.uv.follow_active_quads()
        
        return {'FINISHED'}

class DMR_SMASH_MIRRORVERTEXGROUP(bpy.types.Operator): # ------------------------------
    bl_label = "Mirror Selected Weights"
    bl_idname = 'dmr_smash.mirror_selected_weights'
    bl_description = 'Mirrors weights of selected vertices in group';
    
    def execute(self, context):
        bpy.ops.object.vertex_group_mirror(use_topology = False);
            
        return {'FINISHED'}

class DMR_SMASH_BAKESHAPEKEYS(bpy.types.Operator): # ------------------------------
    bl_label = "Bake Shape Keys"
    bl_idname = 'dmr_smash.bake_shape_keys'
    bl_description = 'Bakes Shape Keys of selected Objects';
    
    keepFinalKey : bpy.props.BoolProperty(name = "Keep Final Key", default = True);
    
    def invoke(self, context, event):
        wm = context.window_manager;
        return wm.invoke_props_dialog(self);
    
    def draw(self, context):
        layout = self.layout;
        layout.prop(self, "keepFinalKey");
        layout.label(text = 'If enabled, result is kept as "Baked"');
    
    def execute(self, context):
        hits = 0;
        
        oldactive = context.active_object;
        
        if len(context.selected_objects) == 0:
            self.report({'WARNING'}, "No objects selected");
            return {'FINISHED'}
        
        for obj in context.selected_objects:
            if obj.type == "MESH":
                # No Shape Keys exist for object
                if obj.data.shape_keys == None:
                    continue;
                
                shape_keys = obj.data.shape_keys.key_blocks;
                
                count = len(shape_keys);
                if count == 0:
                    continue;
                
                bpy.context.view_layer.objects.active = obj;
                
                # Create new Key using existing Keys' values
                bpy.ops.object.shape_key_add(from_mix=True);
                
                # Remove all Keys except for the newly created one
                for i in range(0, count):
                    obj.active_shape_key_index = 0;
                    bpy.ops.object.shape_key_remove(all=False)
                
                # Set new Key's name
                if self.keepFinalKey:
                    shape_keys[0].name = "(Baked)";
                # Remove new Key
                else:
                    bpy.ops.object.shape_key_remove(all = True);
                
                hits += 1;
            
        if hits == 0:
            self.report({'WARNING'}, "No objects modified");
        else:
            self.report({'INFO'}, "%d Object(s) Modified" % hits);
        
        bpy.context.view_layer.objects.active = oldactive;
            
        return {'FINISHED'}

class DMR_SMASH_CLEARWEIGHTS(bpy.types.Operator): # ------------------------------
    bl_label = "Clear Groups From Selected"
    bl_idname = 'dmr_smash.clear_weights_from_selected'
    bl_description = 'Clears all vertex groups from selected vertices';
    
    def execute(self, context):
        selectedObject = context.active_object;
        if selectedObject.type == 'MESH':
            mode = SetViewMode('OBJECT'); # Update Selected
            
            vertexGroups = selectedObject.vertex_groups;
            
            # Remove Groups
            for v in selectedObject.data.vertices:
                if v.select:
                    ClearVertexWeights(v, vertexGroups);
                
            SetViewMode(mode);
            
        return {'FINISHED'}

class DMR_SMASH_CLEANWEIGHTS(bpy.types.Operator): # ------------------------------
    bl_label = "Clean Weights from Selected"
    bl_idname = 'dmr_smash.clean_weights_from_selected'
    bl_description = 'Cleans weights from selected objects';
    
    def execute(self, context):
        mode = SetViewMode('OBJECT'); # Update Selected
        count = 0;
        
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                vertexGroups = obj.vertex_groups;
                
                # Remove Groups
                for v in obj.data.vertices:
                    if v.select:
                        for g in v.groups:
                            # Pop vertex from group
                            if g.weight == 0:
                                vertexGroups[g.group].remove([v.index])
                                count += 1;
        
        self.report({'INFO'}, "Cleaned %s weights" % count);
        
        SetViewMode(mode);
            
        return {'FINISHED'}

class DMR_SMASH_REMOVEEMPTYGROUPS(bpy.types.Operator): # ------------------------------
    bl_label = "Remove Empty Groups"
    bl_idname = 'dmr_smash.remove_empty_groups'
    bl_description = 'Removes Vertex Groups with no weight data';
    
    removeZero : bpy.props.BoolProperty(name = "Ignore Zero Weights", default = True);
    
    def invoke(self, context, event):
        wm = context.window_manager;
        return wm.invoke_props_dialog(self);
    
    def draw(self, context):
        layout = self.layout;
        layout.prop(self, "removeZero");
    
    def execute(self, context):
        selectedObject = context.active_object;
        if selectedObject.type == 'MESH':
            mode = SetViewMode('OBJECT'); # Update Selected
            
            vertexGroups = selectedObject.vertex_groups;
            targetGroups = [v for v in vertexGroups];
            
            # Find and pop groups with vertex data
            for v in selectedObject.data.vertices:
                for g in v.groups:
                    realGroup = vertexGroups[g.group];
                    if realGroup in targetGroups:
                        if g.weight > 0 or not self.removeZero:
                            targetGroups.remove(realGroup);
                    
                if len(targetGroups) == 0:
                    break;
            
            # Remove Empty Groups
            count = len(targetGroups);
            if count == 0:
                self.report({'INFO'}, "No Empty Groups Found");
            else:
                for g in targetGroups:
                    vertexGroups.remove(g);
                self.report({'INFO'}, "Found and removed %d empty group(s)" % count);
            
            SetViewMode(mode);
            
        return {'FINISHED'}

class DMR_SMASH_REMOVERIGHTSIDEGROUPS(bpy.types.Operator): # ------------------------------
    bl_label = "Remove Right Bone Groups"
    bl_idname = 'dmr_smash.clear_right_groups'
    bl_description = 'Removes vertex groups that have a name with "R" as the final letter\nExample: "ShoulderR" will be erased';
    
    def execute(self, context):
        selectedObject = context.active_object;
        if selectedObject.type == 'MESH':
            mode = SetViewMode('OBJECT'); # Update Selected
            
            vertexGroups = selectedObject.vertex_groups;
            
            # Free Right Side Vertices
            for g in vertexGroups:
                if lastLetter(g.name) == "R":
                    vertexGroups.remove(g)
            
            SetViewMode(mode);
        
        return {'FINISHED'}

class DMR_SMASH_DUPLICATEANDMIRROR(bpy.types.Operator): # ------------------------------
    bl_label = "Duplicate and Mirror"
    bl_idname = 'dmr_smash.dup_and_mirror'
    bl_description = 'Duplicates selected vertices and mirrors to other side' + \
        "Performs a Duplication, X Mirror, Remove Doubles, Flip Normals, and Mirror UV" + \
        "NOTE: UVs will be incorrect for overlapping geometry";
    
    def execute(self, context):
        selectedObject = context.active_object;
        if selectedObject.type == 'MESH':
            bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'LINEAR', "proportional_size":0.00813916, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
            
            mode = GetViewMode();
            SetViewMode('OBJECT'); # Update Selected
            SetViewMode(mode);
            
            mesh = selectedObject.data;
            mesh.update();
            
            pivot = bpy.context.scene.tool_settings.transform_pivot_point;
            cursorLoc = (
                context.scene.cursor.location[0],
                context.scene.cursor.location[1],
                context.scene.cursor.location[2]
                );
            bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR';
            context.scene.cursor.location = (0, 0, 0);
            
            bpy.ops.transform.mirror(orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), use_proportional_edit=False, proportional_edit_falloff='LINEAR', proportional_size=0.00813916, use_proportional_connected=True, use_proportional_projected=False)
            #bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.mesh.flip_normals();
            
            mode = GetViewMode();
            SetViewMode('OBJECT'); # Update Selected
            SetViewMode(mode);
            
            bpy.ops.mesh.remove_doubles(threshold=0.00001, use_unselected=True);
            bpy.ops.uv.muv_mirror_uv(axis='X')
            
            bpy.context.scene.tool_settings.transform_pivot_point = pivot;
            context.scene.cursor.location = cursorLoc;
                        
        return {'FINISHED'}

class DMR_SMASH_LEFTGROUPSTORIGHT(bpy.types.Operator): # ------------------------------
    bl_label = "Copy Left Weights to Right"
    bl_idname = 'dmr_smash.copy_right_groups'
    bl_description = 'Takes groups with a final letter of "L", \
    \ncreates a new group with a final letter of "R",\
    \nand mirrors the weights.';
    
    def execute(self, context):
        selectedObject = context.active_object;
        if selectedObject.type == 'MESH':
            mode = SetViewMode('OBJECT'); # Update Selected
            
            print(selectedObject.name)
            
            vertices = selectedObject.data.vertices;
            vertexGroups = selectedObject.vertex_groups;
            oppositeGroup = {}
            
            # Free Right Side Vertices
            for g in vertexGroups:
                if lastLetters(g.name)[0] == "R":
                    vertexGroups.remove(g)
            
            # Create Halved Group
            for g in vertexGroups:
                if lastLetters(g.name)[0] == "L":
                    oppositeGroup[g.index] = vertexGroups.new(name = switchName(g.name) )
            
            validVertices = [];
            oppositeVertex = {}
            
            # Find Opposite Vertices
            for v in vertices:
                if v in validVertices:
                    continue;
                v.select = False;
                for v2 in vertices:
                    if v.undeformed_co.x == -v2.undeformed_co.x \
                    and v.undeformed_co.y == v2.undeformed_co.y \
                    and v.undeformed_co.z == v2.undeformed_co.z:
                        validVertices.append(v)
                        validVertices.append(v2)
                        oppositeVertex[v] = v2;
                        oppositeVertex[v2] = v;
                        break;
            
            # Apply Weights
            for v in validVertices:
                for g in v.groups:
                    if lastLetters(vertexGroups[g.group].name)[0] == "L":
                        v.select = True
                        gIndex = vertexGroups[g.group].index;
                        oppVertex = oppositeVertex[v]
                        oppositeGroup[g.group].add([oppVertex.index], g.weight, 'ADD');
                
            SetViewMode(mode);
        
        return {'FINISHED'}

# Buggy. Disabled
class DMR_SMASH_FACETOSQUARE(bpy.types.Operator): # ------------------------------
    bl_label = "Straighten Face"
    bl_idname = 'dmr_smash.face_to_square'
    bl_description = 'Aligns 4 sided face along the x and y axis.'
    bl_description += '\nUseful for clean results when using "Follow Active Quads"';
    bl_description += '\nDoes NOT work when in "Sync Selection" mode';
    
    def execute(self, context):
        selectedObject = context.active_object;
        
        print("-" * 80)
        
        if selectedObject.type == 'MESH':
            mode = SetViewMode('OBJECT'); # Update Selected
            
            vertexGroups = selectedObject.vertex_groups;
            uvLayers = selectedObject.data.uv_layers;
            
            # Find UVs
            meshdata = selectedObject.data;
            
            center = [0, 0];
            centercount = 0;
            targetLoop = [];
            
            for polygon in meshdata.polygons:
                for i in polygon.loop_indices:
                    meshuvloop = uvLayers.active.data[i];
                    if meshuvloop.select:
                        # Check if corner has been accounted for
                        positionExists = False;
                        for checkedloop in targetLoop:
                            if checkedloop.uv[0] == meshuvloop.uv[0] and \
                            checkedloop.uv[1] == meshuvloop.uv[1]:
                                positionExists = True;
                                break;
                            
                        if not positionExists:
                            center[0] += meshuvloop.uv[0];
                            center[1] += meshuvloop.uv[1];
                            centercount += 1;
                        
                        targetLoop.append(meshuvloop);
            
            if len(targetLoop) == 0:
                self.report({'ERROR'}, "No faces selected");
                SetViewMode(mode);
                return {'FINISHED'}
            
            print(len(targetLoop));
            
            center[0] /= centercount;
            center[1] /= centercount;
            #print(center);
            
            # Find corners
            corner = {};
            corner["TL"] = [];
            corner["TR"] = [];
            corner["BL"] = [];
            corner["BR"] = [];
            
            for loop in targetLoop:
                # Left
                if loop.uv[0] < center[0]:
                    if loop.uv[1] < center[1]: # Top
                        corner["TL"].append(loop);
                    else: # Bottom
                        corner["BL"].append(loop);
                # Right
                else:
                    if loop.uv[1] < center[1]: # Top
                        corner["TR"].append(loop);
                    else: # Bottom
                        corner["BR"].append(loop);
            
            # Check corners
            for looplist in corner.values():
                for looplist2 in corner.values():
                    if looplist == looplist2:
                        continue;
                    if len(looplist2) == 0:
                        self.report({'ERROR'}, "Shape does not resemble a square. Transform selected face such that it loosely resembles an axis aligned square");
                        SetViewMode(mode);
                        return {'FINISHED'}
            
            # Make Sides
            side = [[], [], [], []];
            side[0].extend([l for l in corner["TR"]]);
            side[0].extend([l for l in corner["BR"]]);
            
            side[1].extend([l for l in corner["TL"]]);
            side[1].extend([l for l in corner["TR"]]);
            
            side[2].extend([l for l in corner["TL"]]);
            side[2].extend([l for l in corner["BL"]]);
            
            side[3].extend([l for l in corner["BL"]]);
            side[3].extend([l for l in corner["BR"]]);
            
            # Apply
            i = 0;
            for looplist in side:
                print(len(side))
                sourceuv = [0, 0];
                sourcecount = 0;
                
                for loop in looplist:
                    sourceuv[0] += loop.uv[0];
                    sourceuv[1] += loop.uv[1];
                    sourcecount += 1;
                    
                sourceuv[0] /= sourcecount;
                sourceuv[1] /= sourcecount;
                
                for loop in looplist:
                    if i == 0 or i == 2:
                        loop.uv[0] = sourceuv[0];
                    else:
                        loop.uv[1] = sourceuv[1];
                i += 1;
            
            SetViewMode(mode);
            
            
        return {'FINISHED'}

class DMR_SMASH_CLEARPOSETRANSFORM(bpy.types.Operator): # ------------------------------
    bl_label = "Clear Selected Bones' Keyframes"
    bl_idname = 'dmr_smash.clear_pose_transform'
    bl_description = 'Clears Location/Rotation/Scale keyframes from selected pose bones' + \
        "\nNOTE: Has not been tested in a while. May not work";
    
    isSimple : bpy.props.BoolProperty(name = "Simple", default = True);
    
    simpleLoc : bpy.props.BoolProperty(name = "Location", default = False);
    simpleRot : bpy.props.BoolProperty(name = "Rotation", default = False);
    simpleSca : bpy.props.BoolProperty(name = "Scale", default = False);
    
    locX : bpy.props.BoolProperty(name = "Location X", default = False);
    locY : bpy.props.BoolProperty(name = "Location Y", default = False);
    locZ : bpy.props.BoolProperty(name = "Location Z", default = False);
    
    rotX : bpy.props.BoolProperty(name = "Rotation X", default = False);
    rotY : bpy.props.BoolProperty(name = "Rotation Y", default = False);
    rotZ : bpy.props.BoolProperty(name = "Rotation Z", default = False);
    rotW : bpy.props.BoolProperty(name = "Rotation W", default = False);
    
    scaX : bpy.props.BoolProperty(name = "Scale X", default = False);
    scaY : bpy.props.BoolProperty(name = "Scale Y", default = False);
    scaZ : bpy.props.BoolProperty(name = "Scale Z", default = False);
    
    processWhole : bpy.props.BoolProperty(name = "Process Entire Action", default = False);
    keyframeRangeMin : bpy.props.IntProperty(name = "", default = 0);
    keyframeRangeMax : bpy.props.IntProperty(name = "", default = 60);
    
    def invoke(self, context, event):
        wm = context.window_manager;
        return wm.invoke_props_dialog(self);
    
    def draw(self, context):
        layout = self.layout;
        
        layout.prop(self, "isSimple");
        
        # Transforms
        if self.isSimple:
            box = layout.box();
            box.label(text = "Transform Type");
            row = box.row();
            row.prop(self, "simpleLoc");
            row.prop(self, "simpleRot");
            row.prop(self, "simpleSca");
        else:
            box = layout.box();
            box.label(text = "Transform Type & Channel");
            row = box.row();
            row.prop(self, "locX"); row.prop(self, "rotX"); row.prop(self, "scaX");
            
            row = box.row();
            row.prop(self, "locY"); row.prop(self, "rotY"); row.prop(self, "scaY");
            
            row = box.row();
            row.prop(self, "locZ"); row.prop(self, "rotZ"); row.prop(self, "scaZ");
            row = box.row();
            row.prop(self, "rotW");
        
        # Range
        layout.prop(self, "processWhole");
        
        if not self.processWhole:
            section = layout.box();
            row = section.row();
            row.label(text = "Keyframe Range");
            row.prop(self, "keyframeRangeMin");
            row.prop(self, "keyframeRangeMax");
        
    
    def execute(self, context):
        context = bpy.context;
        selectedObject = context.active_object;
        
        # Checks
        bail = False;
        if selectedObject.type != 'ARMATURE':
            self.report({'ERROR'}, "Selected Object is not an Armature");
            bail = True;
        
        action = selectedObject.animation_data.action;
        
        if action == None:
            self.report({'ERROR'}, "Invalid action");
            bail = True;
        
        targetTransform = [[], [], []];
        
        if self.isSimple:
            if self.simpleLoc:
                targetTransform[0].extend([0, 1, 2]);
            if self.simpleRot:
                targetTransform[1].extend([0, 1, 2, 3]);
            if self.simpleSca:
                targetTransform[2].extend([0, 1, 2]);
        else:
            if self.locX:
                targetTransform[0].append(0);
            if self.locY:
                targetTransform[0].append(1);
            if self.locZ:
                targetTransform[0].append(2);
            if self.rotX:
                targetTransform[1].append(0);
            if self.rotY:
                targetTransform[1].append(1);
            if self.rotZ:
                targetTransform[1].append(2);
            if self.rotW:
                targetTransform[1].append(3);
            if self.scaX:
                targetTransform[2].append(0);
            if self.scaY:
                targetTransform[2].append(1);
            if self.scaZ:
                targetTransform[2].append(2);
        
        if len(targetTransform[0]) == 0 and len(targetTransform[1]) == 0 and len(targetTransform[2]) == 0:
            self.report({'WARNING'}, 'No transforms selected for "' + self.bl_label + '"');
            bail = True;
        
        minFrame = self.keyframeRangeMin;
        maxFrame = self.keyframeRangeMax;
        
        if minFrame > maxFrame:
            self.report({'WARNING'}, 'Range corrected for operation "' + self.bl_label + '"');
            temp = minFrame;
            minFrame = maxFrame;
            maxFrame = temp;
        
        if bail:
            return {'FINISHED'}
        
        # Determine what to yeet
        transformdict = {"location" : 0, "rotation_quaternion" : 1, "scale" : 2}
        transformnamelist = ["Loc", "Rot", "Sca"];
        
        print("Action: " + action.name);
        
        # Execution
        objectmode = SetViewMode('OBJECT'); # Update Selected
        
        selectedBones = [];
        for bone in selectedObject.data.bones:
            if bone.select and not bone.hide:
                selectedBones.append(bone.name);
        
        for fcu in action.fcurves:
            #print(fcu.data_path + " channel " + str(fcu.array_index))
            
            bonename = "";
            path = fcu.data_path;
            pos = [-1, 0];
            
            # Find string positions
            for i in range(0, len(path)):
                if path[i] == '"':
                    # Start of string
                    if pos[0] == -1:
                        pos[0] = i + 1;
                    else:
                        pos[1] = i;
            
            transformname = path[pos[1] + 3:];
            
            # Skip transforms that aren't in dict
            if transformname not in transformdict:
                continue;
            
            bonename = path[pos[0]:pos[1]];
            
            # Skip bones that aren't not selected
            if bonename not in selectedBones:
                continue;
            
            transformtype = transformdict[transformname];
            transformchannel = fcu.array_index;
            
            # Skip if transform is not target
            if transformchannel not in targetTransform[transformtype]:
                continue;
            
            print(bonename + " " + transformnamelist[transformtype] + "[" + str(transformchannel) + "]" + ", Keyframes: " + str(len(fcu.keyframe_points)));
            
            # Delete all keyframes for given transform channel
            if self.processWhole:
                print("- Clearing all keyframes");
                action.fcurves.remove(fcu);
            # Delete frames in range
            else:
                keyframelist = [];
                for k in fcu.keyframe_points:
                    keyframelist.append(k);
                
                for k in keyframelist:
                    print("- Keyframe %s" % k.co[0]);
                    if k.co[0] >= minFrame and k.co[0] <= maxFrame:
                        fcu.keyframe_points.remove(k);
                

        print("=" * 40);
        
        SetViewMode(objectmode);
            
        return {'FINISHED'}

class DMR_SMASH_BONE_MATCH_MIRROR(bpy.types.Operator): # ------------------------------
    bl_label = "Match Bone Mirror"
    bl_idname = 'dmr_smash.bone_match_mirror'
    bl_description = 'Matches positions of selected bones with their mirror based on the last letter\nEx: "KneeR" will be matched to "KneeL"\nNOTE: Does not calculate roll';
    
    def execute(self, context):
        selectedObject = context.active_object;
        
        if selectedObject.type != 'ARMATURE':
            self.report({'WARNING'}, 'No armature selected"');
        
        objectmode = SetViewMode('OBJECT'); # Update Selected
        SetViewMode(objectmode);
        
        print("> Reading Armature \"" + selectedObject.name + "\"...")
        
        editBones = selectedObject.data.edit_bones;
        targetLetter = None;
        hits = 0;
        
        print(len(editBones));
        
        # Find selected bones
        for bone in editBones:
            if bone.select:
                if lastLetters(bone.name)[0] not in ["L", "R"]:
                    continue;        
                
                targetName = switchName(bone.name);
                if targetName in editBones:
                    mirrorBone = editBones[targetName];
                    print("%s -> %s" % (bone.name, mirrorBone.name));
                    bone.head.x = -mirrorBone.head.x;
                    bone.head.y = mirrorBone.head.y;
                    bone.head.z = mirrorBone.head.z;
                    
                    bone.tail.x = -mirrorBone.tail.x;
                    bone.tail.y = mirrorBone.tail.y;
                    bone.tail.z = mirrorBone.tail.z;
                    hits += 1;
        
        self.report({'INFO'}, 'Matched %d Bone(s)"' % hits);
        
        return {'FINISHED'}

# -------------------------------------------------------------------

def dmr_matchDraw(op, context, plural):
    layout = op.layout;
    
    section = layout.column();
    section.prop(op, "matchInGroup");
    if op.matchInGroup:
        section = section.box();
        section.label(text = "Source Vertex Group");
        section.prop(op, "groupname");
    
    section = layout.row();
    section.label(text = "Match Distance");
    section.prop(op, "testRange");
    
    sourcename = "";
    column = layout.column();
    
    # Draw selected object names
    if len(context.selected_objects) <= 1:
        column.label(text = "<Need at least 2 objects selected>");
    else:
        objlist = "";
        activeObject = context.object;
        column.label(text = '"' + activeObject.name + '"' + "'s " + plural + " to...");
        for selectedObject in context.selected_objects:
            if selectedObject == activeObject:
                continue;
            if activeObject.type != 'MESH':
                continue;
            column.label(text = "  >" + selectedObject.name);

def dmr_matchPre(self, context):
    activeObject = context.object;
    
    # Check if Mesh
    if activeObject.type != 'MESH':
        self.report({'WARNING'}, 'Active object "%s" is not a mesh' % activeObject.name);
        return False;
    
    # Check if there's selected
    if len(context.selected_objects) <= 1:
        self.report({'WARNING'}, 'Need at least 2 objects selected');
        return False;
    
    # Check for vertex group if needed
    if self.matchInGroup:
        if self.groupname not in activeObject.vertex_groups.keys():
            self.report({'WARNING'}, 'Vertex Group "%s" not found in "%s"' % (self.groupname, activeObject.name));
            return False;
    
    return True;

class DMR_SMASH_MATCHVERTEX(bpy.types.Operator): # ------------------------------
    bl_label = "Match Vertex"
    bl_idname = 'dmr_smash.match_vertex'
    bl_description = 'Matches vertex positions of selected objects to those of the active object based on closeness';
    bl_description += '\nNOTE: Vertex offsets are based off of origin';
    bl_description += '\nNOTE: Does NOT work if selected mesh has shape keys. Use Inner Vertex Match in that case';
    
    matchInGroup : bpy.props.BoolProperty(name = "Only Match In Vertex Group", default = False);
    groupname : bpy.props.StringProperty(name = "", default = "vertex");
    testRange : bpy.props.FloatProperty(name = "", default = 0.01, precision = 4);
    
    def invoke(self, context, event):
        wm = context.window_manager;
        return wm.invoke_props_dialog(self);
    
    def draw(self, context):
        dmr_matchDraw(self, context, "vertices");
        
    def execute(self, context):
        if not dmr_matchPre(self, context):
            return {'FINISHED'}
        
        activeObject = context.object;
        rangeAmount = self.testRange;
        hits = 0;
        modifiedhits = 0;
        
        mode = SetViewMode('OBJECT'); # Update Selected
        
        # Find source vertices
        sourceVertices = activeObject.data.vertices;
        if self.matchInGroup:
            sourceVertices = FindVertexGroupVertices(activeObject, self.groupname);
        
        print(len(sourceVertices));
        
        # Find objects
        for selectedObject in context.selected_objects:
            if (selectedObject == activeObject) or (selectedObject.type) != 'MESH':
                continue;
            
            print("\t" + selectedObject.name)
            
            # Match
            for v in selectedObject.data.vertices:
                sv = FindClosestVertex(v, sourceVertices, rangeAmount);
                hits += 1;
                
                if sv != None:
                    print(sv);
                    if (v.co[0] != sv.co[0]) or (v.co[1] != sv.co[1]) or (v.co[2] != sv.co[2]):
                        modifiedhits += 1;
                    v.co = (sv.co[0], sv.co[1], sv.co[2]);
                    print(v.co);
                    
        
        self.report({'INFO'}, 'Modified %d out of %d Vertices(s) sourced from "%s"' % (modifiedhits, hits, activeObject.name));
        SetViewMode(mode);
        
        return {'FINISHED'}

class DMR_SMASH_MATCHVERTEXINNER(bpy.types.Operator): # ------------------------------
    bl_label = "Match Vertex Inner"
    bl_idname = 'dmr_smash.match_vertex_inner'
    bl_description = 'Matches vertex positions of unselected selected vertices to those of selected based on closeness';
    
    testRange : bpy.props.FloatProperty(name = "", default = 0.01, precision = 4);
    
    def invoke(self, context, event):
        wm = context.window_manager;
        return wm.invoke_props_dialog(self);
    
    def draw(self, context):
        layout = self.layout;
        
        section = layout.row();
        section.label(text = "Match Distance");
        section.prop(self, "testRange");
        
    def execute(self, context):
        activeObject = context.object;
        rangeAmount = self.testRange;
        hits = 0;
        modifiedhits = 0;
        
        mode = SetViewMode('OBJECT'); # Update Selected
        SetViewMode('EDIT');
        
        # Find source and target vertices
        sourceVertices = [];
        targetVertices = [];
        
        for v in activeObject.data.vertices:
            if v.select:
                sourceVertices.append(v);
            else:
                targetVertices.append(v);
            v.select = False;
        
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR';
        
        # Match
        for v in targetVertices:
            sv = FindClosestVertex(v, sourceVertices, rangeAmount);
            
            if sv != None:
                hits += 1;
                
                if (v.co[0] != sv.co[0]) or (v.co[1] != sv.co[1]) or (v.co[2] != sv.co[2]):
                    modifiedhits += 1;
                
                #v.co = (sv.co[0], sv.co[1], sv.co[2]);
                #print(v.co);
                
                v.select = True;
                context.scene.cursor.location = (sv.co[0], sv.co[1], sv.co[2]);
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=False);
                v.select = False;
        
        self.report({'INFO'}, 'Modified %d out of %d Vertices(s)' % (modifiedhits, hits));
        SetViewMode(mode);
        
        return {'FINISHED'}

class DMR_SMASH_MATCHNORMALS(bpy.types.Operator): # ------------------------------
    bl_label = "Match Normals"
    bl_idname = 'dmr_smash.match_normals'
    bl_description = 'Matches normals of selected objects to those of the active object based on closeness of vertices' + \
    '\nUseful for correcting normals on detetched face expression meshes.' + \
    '\n"Auto Smooth" for selected meshes must be enabled for custom normals.' + \
    '\nNOTE: Vertex offsets are based off of origin';
    
    matchInGroup : bpy.props.BoolProperty(name = "Only Match In Vertex Group", default = False);
    groupname : bpy.props.StringProperty(name = "", default = "normal");
    testRange : bpy.props.FloatProperty(name = "", default = 0.01, precision = 4);
    
    def invoke(self, context, event):
        wm = context.window_manager;
        return wm.invoke_props_dialog(self);
    
    def draw(self, context):
        dmr_matchDraw(self, context, "normals");
    
    def execute(self, context):
        if not dmr_matchPre(self, context):
            return {'FINISHED'}
        
        activeObject = context.object;
        rangeAmount = self.testRange;
        hits = 0;
        
        mode = SetViewMode('OBJECT'); # Update Selected
        
        # Find source vertices
        sourceVertices = activeObject.data.vertices;
        if self.matchInGroup:
            sourceVertices = FindVertexGroupVertices(activeObject, self.groupname);
        
        # Find objects
        for selectedObject in context.selected_objects:
            if selectedObject == activeObject or selectedObject.type != 'MESH':
                continue;
            
            # Match Normals
            normals = [];
            
            for v in selectedObject.data.vertices:
                n = v.normal;
                v2 = FindClosestVertex(v, sourceVertices, rangeAmount);
                
                if v2 != None:
                    hits += 1;
                    n = v2.normal;
                normals.append(n);
            
            # Apply
            selectedObject.data.normals_split_custom_set_from_vertices(normals);
        
        self.report({'INFO'}, 'Matched Normals for %d Vertices(s) sourced from "%s"' % (hits, activeObject.name));
        SetViewMode(mode);
        
        return {'FINISHED'}

class DMR_SMASH_MATCHWEIGHTS(bpy.types.Operator): # ------------------------------
    bl_label = "Match Weights"
    bl_idname = 'dmr_smash.match_weights'
    bl_description = 'Matches vertex weights of selected objects to those of the active object based on closeness';
    bl_description += '\nNOTE: Vertex offsets are based off of origin';
    
    matchInGroup : bpy.props.BoolProperty(name = "Only Match In Vertex Group", default = False);
    groupname : bpy.props.StringProperty(name = "", default = "weights");
    testRange : bpy.props.FloatProperty(name = "", default = 0.01, precision = 4);
    
    def invoke(self, context, event):
        wm = context.window_manager;
        return wm.invoke_props_dialog(self);
    
    def draw(self, context):
        dmr_matchDraw(self, context, "weights");
    
    def execute(self, context):
        if not dmr_matchPre(self, context):
            return {'FINISHED'}
        
        activeObject = context.object;
        rangeAmount = self.testRange;
        hits = 0;
        weighthits = 0;
        
        mode = SetViewMode('OBJECT'); # Update Selected
        
        # Find source vertices
        sourceVertices = activeObject.data.vertices;
        if self.matchInGroup:
            sourceVertices = FindVertexGroupVertices(activeObject, self.groupname);
        
        sourceGroups = activeObject.vertex_groups;
        sourceGroupNames = [g.name for g in sourceGroups];
        
        # Find objects
        for selectedObject in context.selected_objects:
            if selectedObject == activeObject or selectedObject.type != 'MESH':
                continue;
            
            otherGroups = selectedObject.vertex_groups;
            otherGroupsNames = [g.name for g in sourceGroups];
            
            # Match (v = other, sourceVertex = source)
            for v in selectedObject.data.vertices:
                sourceVertex = FindClosestVertex(v, sourceVertices, rangeAmount);
                
                if sourceVertex != None:
                    ClearVertexWeights(v, otherGroups);
                    hits += 1;
                    
                    for vge2 in sourceVertex.groups:
                        SetVertexWeight(v, vge2.weight, sourceGroups[vge2.group].name, otherGroups);
                        weighthits += 1;
        
        self.report({'INFO'}, 'Matched %d Weights(s) for %s Vertice(s) sourced from "%s"' % (weighthits, hits, activeObject.name));
        SetViewMode(mode);
        
        return {'FINISHED'}

# -------------------------------------------------------------------

class DMR_SMASH_ALIGN(bpy.types.Operator): # ------------------------------
    bl_label = "Quick Align"
    bl_idname = 'dmr_smash.uv_align'
    bl_description = 'Runs "Align" on selected vertices';
    
    def execute(self, context):
        bpy.ops.uv.align();
        return {'FINISHED'}

class DMR_SMASH_RESET3DCURSOR(bpy.types.Operator): # ------------------------------
    bl_label = "Reset 3D Cursor"
    bl_idname = 'dmr_smash.reset_3dcursor'
    bl_description = 'Resets 3D cursor to (0, 0, 0)';
    
    def execute(self, context):
        context.scene.cursor.location = (0.0, 0.0, 0.0)
        return {'FINISHED'}

class DMR_SMASH_CLEANMATERIALS(bpy.types.Operator): # ------------------------------
    bl_label = "Clean Materials"
    bl_idname = 'dmr_smash.clean_materials'
    bl_description = 'Removes materials that have no users';
    
    def execute(self, context):
        
        targetMaterials = [m for m in bpy.data.materials];
        print("-" * 80)
        # Find used materials
        for obj in context.scene.objects:
            for m in obj.material_slots:
                if m.material in targetMaterials:
                    targetMaterials.remove(m.material);
        
        # Delete unused materials
        hits = len(targetMaterials);
        if hits == 0:
            self.report({'INFO'}, 'No materials removed');
        else:
            for m in targetMaterials:
                print('Removing "%s"' % m.name);
                bpy.data.materials.remove(m)
            self.report({'INFO'}, 'Removed %s Materials' % hits);
            
        return {'FINISHED'}

class DMR_SMASH_SMDPRIME(bpy.types.Operator): # ------------------------------
    bl_label = "Prime Data for SMD"
    bl_idname = 'dmr_smash.prime_for_smd'
    bl_description = 'Targets objects with given prefix.';
    bl_description += '\nRenames meshes to their object name with a lowercase starting letter' + \
    '\nRenames object materials to the object name';
    
    targetname : bpy.props.StringProperty(name = "Model Prefix", default = "Wiz");
    charname : bpy.props.StringProperty(name = "VIS Name", default = "zelda");
    
    ophelp : bpy.props.BoolProperty(name = "Help", default = False);
    
    def invoke(self, context, event):
        wm = context.window_manager;
        return wm.invoke_props_dialog(self);
    
    def draw(self, context):
        layout = self.layout;
        
        layout.label(text = "Prefix of object names");
        layout.prop(self, "targetname");
        layout.label(text = "Name to replace prefix with for VIS objects");
        layout.prop(self, "charname");
        
        box = layout.box().column();
        box.prop(self, "ophelp");
        
        if self.ophelp:
            box.label(text = "Material names are created based on");
            box.label(text = "the case of the first letter of an object's name.");
            box.label(text = "Uppcase -> Mat Name = Object name");
            box.label(text = "Lowcase -> Mat Name = Prefix swapped with VIS name");
            box = layout.box().column();
            box.label(text = 'Ex: with Model Prefix = "Wiz", VIS Name = "zelda"');
            box.label(text = '"Wiz_Hair" -> "Wiz_Hair"');
            box.label(text = '"wiz_Hot_VIS_O_OBJShape" -> "zelda_Hot_VIS_O_OBJShape"');
    
    def execute(self, context):
        namestart = str(self.targetname[0]);
        
        TARGETNAME = namestart.upper() + self.targetname[1:];
        TARGETNAME2 = namestart.lower() + self.targetname[1:];
        CHARNAME = self.charname;
        
        print("=" * 100)
        
        matDict = {};
        matCountDict = {};
        targetObjects = [];
        
        def getNodeCount(nodes):
            if len(nodes) == 0:
                return 1;
            for n in nodes:
                return getNodeCount(n);
        
        # Find Material Names
        for obj in bpy.data.objects:
            if obj.type != 'MESH': continue;
            if obj.name[:len(TARGETNAME)] != TARGETNAME and \
            obj.name[:len(TARGETNAME)] != TARGETNAME2: continue;
            
            targetObjects.append(obj);
            
            mat = obj.active_material;
            if mat == None: continue;
            
            if mat.name not in matCountDict:
                matCountDict[mat.name] = [obj.name];
                matDict[mat.name] = mat;
            else:
                matCountDict[mat.name].append(obj.name);
            
            obj.data.name = "mesh_" + obj.name;
            obj.select_set(False);
            #print("%s: %s" % (obj.name, obj.active_material));
        
        # Report Materials
        print("%d Materials Found" % len(matCountDict));
        problemMat = [];
        for name in matCountDict.keys():
            if len(matCountDict[name]) > 1:
                problemMat.append(matDict[name]);
        
        infostring = "";
        infotype = 'INFO';
        
        if len(problemMat) != 0:
            print("%d Non-Unique Materials found" % len(problemMat));
            print('Click the "New Material" button in the Material tab for the following materials' + 
            '\nafter making Node Groups for node structures');
            problemnames = "";
            for mat in problemMat:
                print(mat.name);
                for objname in matCountDict[mat.name]:
                    print("\t%s" % objname)
                    problemnames += objname + ", ";
                    
                    # Remove problem objects from material check
                    for obj in targetObjects:
                        if obj.name == objname:
                            obj.select_set(True);
                            targetObjects.remove(obj)
                            break;
            
            infotype = 'WARNING';
            infostring = " | These objects have non-unique materials: " + problemnames;
            
            #return {'FINISHED'}
        
        # Update Material Names & Report Objects
        for obj in targetObjects:
            obj.select_set(True);
            newname = TARGETNAME + obj.name[len(TARGETNAME):];
            # Object name has lowercase of target name
            if obj.name[:len(TARGETNAME2)] == TARGETNAME2:
                newname = CHARNAME + obj.name[len(TARGETNAME2):];
            # Print update if name is different
            if obj.active_material.name != newname:
                print('Changing material "%s" of Object "%s" to "%s"' % (obj.active_material.name, obj.name, newname));
                obj.active_material.name = newname;
            print(newname)
        
        infostring = ("Modified %d object names" % len(targetObjects)) + infostring;
        self.report({infotype}, infostring);
            
        return {'FINISHED'}

class DMR_SMASH_DELETEINVERTEXGROUP(bpy.types.Operator): # ------------------------------
    bl_label = "Delete Vertices in Vertex Group"
    bl_idname = 'dmr_smash.remove_vertices_in_group'
    bl_description = 'Deletes vertices in named vertex group for selected objects';
    
    groupname : bpy.props.StringProperty(name = "Group Name", default = "");
    
    def invoke(self, context, event):
        wm = context.window_manager;
        return wm.invoke_props_dialog(self);
    
    def draw(self, context):
        layout = self.layout;
        layout.prop(self, "groupname");
    
    def execute(self, context):
        selectedObject = context.active_object;
        
        mode = SetViewMode('OBJECT'); # Update Selected
        
        hits = 0;
        objecthits = 0;
        
        for selectedObject in context.selected_objects:
            if selectedObject.type == 'MESH':
                SetViewMode('OBJECT');
                
                targetVerts = FindVertexGroupVertices(selectedObject, self.groupname);
                
                if len(targetVerts) == 0:
                    continue;
                
                objecthits += 1;
                
                # Deselect all vertices
                for v in selectedObject.data.vertices:
                    v.select = False;
                
                # Select all vertices in group
                for v in targetVerts:
                    v.select = True;
                    hits += 1;
                
                # Delete selected
                SetViewMode('EDIT');
                bpy.ops.mesh.delete(type='VERT');
                SetViewMode('OBJECT');
                
        SetViewMode(mode);
        
        if objecthits == 0:
            self.report({"WARNING"}, "No objects with specified group found.");
        elif hits == 0:
            self.report({"WARNING"}, "No vertices in specified group found.");
        else:
            self.report({"INFO"}, "%d vertices modified total in %d objects" % (hits, objecthits));
        
        return {'FINISHED'}

class DMR_SMASH_CORRECTWEIGHTS(bpy.types.Operator): # ------------------------------
    bl_label = "Correct Right Weights"
    bl_idname = 'dmr_smash.correct_weights'
    bl_description = "Syncs right side weights to left side's. Works for multiple objects.";
    bl_description += "\nCreates new vertex groups for mirrored sides where needed."
    bl_description += "\nMagic formula for all your weight mirroring woes (Assuming your mesh is centered about its pivot)."
    
    def execute(self, context):
        print("-" * 80)
        
        # BY "RIGHT" I MEAN FROM THE MODEL's POINT OF VIEW!
        
        mode = GetViewMode();
        SetViewMode('OBJECT'); # Update Selected
        
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue;
            
            # Init data
            sourceVertices = obj.data.vertices;
            vertexList = [x for x in obj.data.vertices];
            vertexGroups = {}
            
            for vg in obj.vertex_groups:
                vertexGroups[vg.name] = vg;
                vertexGroups[vg.index] = vg;
            
            # Make swapped groups
            oppositeGroups = {};
            
            for vg in obj.vertex_groups:
                if lastLetter(vg.name) in ["R", "L"]:
                    swapname = switchName(vg.name);
                    print("%s -> %s" % (vg.name, swapname));
                    
                    # Add vertex group if doesn't exist
                    if swapname not in vertexGroups.keys():
                        newgroup = obj.vertex_groups.new(name = swapname);
                        vertexGroups[newgroup.index] = newgroup;
                        vertexGroups[newgroup.name] = newgroup;
                    
                    oppositeGroups[vg.name] = vertexGroups[swapname];
                    oppositeGroups[vg.index] = vertexGroups[swapname];
                else:
                    oppositeGroups[vg.name] = vg;
                    oppositeGroups[vg.index] = vg;
                    print(vg.name);
            
            # Run through vertices
            hits = 0;
            
            for v in obj.data.vertices:
                # Vertex has been checked
                if v not in vertexList:
                    continue;
                
                # Vertex is centered (No mirror chance)
                if v.co[0] == 0.0:
                    hits += 1;
                    vertexList.remove(v);
                    continue;
                
                # Vertex is on right side
                if v.co[0] < 0.0:
                    vertexList.remove(v);
                    vx = -v.co[0];
                    
                    # Find opposite vertex
                    for vSource in vertexList:
                        if vSource.co[0] == vx:
                            vertexList.remove(vSource);
                            hits += 2;
                            
                            # Clear all weights for right vert
                            ClearVertexWeights(v, vertexGroups);
                            
                            # For each group in left (source) vertex....
                            for vge2 in vSource.groups:
                                # Update weights for opposite group
                                oppositeGroups[vge2.group].add([v.index], vge2.weight, 'ADD');
                            break;
            
            info = "%d / %d Vertex Hit(s) for %s" % (hits, len(obj.data.vertices), obj.name);
            self.report({'INFO'}, info);
            
            # Clean Weights
            for v in obj.data.vertices:
                for vge in v.groups:
                    vertsToDelete = [];
                    if vge.weight == 0.0:
                        vertsToDelete.append(v.index);
                    vertexGroups[vge.group].remove(vertsToDelete);
        
        SetViewMode(mode);
        
        return {'FINISHED'}

class DMR_SMASH_WEIGHTSTOSELECTED(bpy.types.Operator): # ------------------------------
    bl_label = "Match Unselected Weights"
    bl_idname = 'dmr_smash.weights_to_selected'
    bl_description = "Matches unselected vertex weights to selected vertices.";
    
    def execute(self, context):
        print("-" * 80)
        
        # BY "RIGHT" I MEAN FROM THE MODEL's POINT OF VIEW!
        
        activeObject = context.active_object;
        
        if activeObject == None:
            self.report({'ERROR'}, "No object selected");
            return {'FINISHED'}
        
        if activeObject.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh");
            return {'FINISHED'}
        
        mode = activeObject.mode;
        SetViewMode('OBJECT'); # Update Selected
        
        vertexSelected = [];
        vertexUnselected = [];
        
        vertexGroups = activeObject.vertex_groups;
        groupCount = len(vertexGroups);
        
        # Find selected and unselected
        for v in activeObject.data.vertices:
            if v.select:
                vertexSelected.append(v);
            else:
                vertexUnselected.append(v);
        
        # Match weights
        hits = 0;
        
        for v in vertexSelected:
            otherVertices = FindClosestVertices(v, vertexUnselected, 0.01);
            
            for v2 in otherVertices:
                vertexUnselected.remove(v2);
                
                # Clear all weights for other vert
                for vge2 in v2.groups:
                    if vge2.group < 0 or vge2.group >= groupCount:
                        continue;
                    vertexGroups[vge2.group].remove([v2.index]);
                
                # For each group in selected vertex...
                for vge in v.groups:
                    # Update weights for unselected group
                    vertexGroups[vge.group].add([v2.index], vge.weight, 'ADD');
                hits += 1;
        
        self.report({'INFO'}, "%d Vertex Weights Matched" % hits);
        
        SetViewMode(mode);
        
        return {'FINISHED'}

class DMR_SMASH_SNAPVERTEX(bpy.types.Operator): # ------------------------------
    bl_label = "Snap Unselected Vertices"
    bl_idname = 'dmr_smash.snap_vertices'
    bl_description = 'Snaps unselected vertices to selected based on closeness' + \
        '\nNOTE: May not work for objects with Shape Keys';
    
    testRange : bpy.props.FloatProperty(name = "", default = 0.001, precision = 4);
    
    def invoke(self, context, event):
        wm = context.window_manager;
        return wm.invoke_props_dialog(self);
    
    def draw(self, context):
        layout = self.layout;
        
        row = layout.row();
        row.label(text = "Match Distance");
        row.prop(self, "testRange");
        
        sourcename = "";
        column = layout.column();
    
    def execute(self, context):
        print("-" * 80)
        
        activeObject = context.object;
        
        if activeObject.type != 'MESH':
            self.report({'WARNING'}, 'Active object "%s" is not a mesh' % activeObject.name);
            return {'FINISHED'}
        
        rangeAmount = self.testRange;
        hits = 0;
        
        mode = GetViewMode();
        SetViewMode('OBJECT'); # Update Selected
        
        selectedVertices = [];
        unselectedVertices = [];
        
        # Sort selected and unselected
        for v in activeObject.data.vertices:
            if v.select:
                selectedVertices.append(v);
            else:
                unselectedVertices.append(v);
        
        # Find and snap
        for v in selectedVertices:
            closestVertices = FindClosestVertices(v, unselectedVertices, rangeAmount);
            
            for v2 in closestVertices:
                unselectedVertices.remove(v2);
                v2.co = (v.co[0], v.co[1], v.co[2]);
                hits += 1;
        
        self.report({'INFO'}, 'Snapped %d Vertices(s)' % hits);
        SetViewMode(mode);
        
        return {'FINISHED'}

# Register =====================================================

classlist = [
    DmrSmashToolsPanel,
    DmrSmashToolsUVPanel,
    
    DMR_SMASH_SNAPSELECTIONTOACTIVE,
    DMR_SMASH_DUPLICATEANDMIRROR,
    DMR_SMASH_TOGGLEPOSE,
    DMR_SMASH_BONE_MATCH_MIRROR,
    DMR_SMASH_CLEARPOSETRANSFORM,
    DMR_SMASH_LEFTGROUPSTORIGHT,
    DMR_SMASH_MIRRORVERTEXGROUP,
    DMR_SMASH_CLEANWEIGHTS,
    DMR_SMASH_CLEARWEIGHTS,
    DMR_SMASH_REMOVEEMPTYGROUPS,
    DMR_SMASH_EDITMODEWEIGHTS,
    DMR_SMASH_REMOVERIGHTSIDEGROUPS,
    DMR_SMASH_MATCHVERTEX,
    DMR_SMASH_MATCHNORMALS,
    DMR_SMASH_MATCHWEIGHTS,
    DMR_SMASH_MATCHVERTEXINNER,
    DMR_SMASH_SMDPRIME,
    DMR_SMASH_BAKESHAPEKEYS,
    DMR_SMASH_DELETEINVERTEXGROUP,
    DMR_SMASH_CORRECTWEIGHTS,
    DMR_SMASH_WEIGHTSTOSELECTED,
    DMR_SMASH_SNAPVERTEX,
    
    DMR_SMASH_ALIGN,
    DMR_SMASH_FOLLOWQUADS,
    #DMR_SMASH_FACETOSQUARE,
    
    DMR_SMASH_IMGRELOAD,
    DMR_SMASH_RESET3DCURSOR,
    DMR_SMASH_PLAYANIM,
    
    # Non Buttons --------------------------
    DMR_SMASH_CLEANMATERIALS,
    ]

def register():
    for op in classlist:
        bpy.utils.register_class(op);

def unregister():
    for op in classlist:
        bpy.utils.unregister_class(op);

if __name__ == "__main__":
    register()

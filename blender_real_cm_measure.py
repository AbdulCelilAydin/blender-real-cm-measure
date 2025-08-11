bl_info = {
    "name": "Real CM Measurement",
    "author": "AbdulCelilAydin",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Real CM",
    "description": "Show and set real-world dimensions in centimeters",
    "category": "3D View",
}

import bpy
from mathutils import Vector

# ----- SCENE SETUP -----
class RCM_OT_SetUnits(bpy.types.Operator):
    bl_idname = "rcm.set_units"
    bl_label = "Set Scene to cm"
    bl_description = "Set scene units to Metric (cm)"

    def execute(self, context):
        sc = context.scene
        sc.unit_settings.system = 'METRIC'
        sc.unit_settings.scale_length = 0.01  # 1 BU = 1 m → display as cm
        try:
            sc.unit_settings.length_unit = 'CENTIMETERS'
        except AttributeError:
            pass
        self.report({'INFO'}, "Scene units set to centimeters")
        return {'FINISHED'}


# ----- SCALE TO CM -----
class RCM_OT_ScaleToCM(bpy.types.Operator):
    bl_idname = "rcm.scale_to_cm"
    bl_label = "Scale Selected to Target cm"
    bl_description = "Scale selected mesh objects so max dimension matches target cm"

    def execute(self, context):
        target_cm = context.scene.rcm_target_cm
        target_m = target_cm / 100.0
        objs = [o for o in context.selected_objects if o.type == 'MESH']
        if not objs:
            self.report({'WARNING'}, "No mesh objects selected")
            return {'CANCELLED'}

        for obj in objs:
            dims = obj.dimensions
            max_dim = max(dims)
            if max_dim == 0:
                continue
            factor = target_m / max_dim
            obj.scale = Vector((obj.scale.x * factor,
                                obj.scale.y * factor,
                                obj.scale.z * factor))
            # Apply scale
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        self.report({'INFO'}, f"Scaled {len(objs)} object(s) to {target_cm} cm")
        return {'FINISHED'}


# ----- UI PANEL -----
class RCM_PT_Panel(bpy.types.Panel):
    bl_label = "Real CM"
    bl_idname = "RCM_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Real CM'

    def draw(self, context):
        layout = self.layout
        layout.operator("rcm.set_units", icon='EMPTY_ARROWS')

        obj = context.active_object
        if obj and obj.type == 'MESH':
            dims_cm = [d * 100 for d in obj.dimensions]
            layout.label(text=f"X: {dims_cm[0]:.2f} cm")
            layout.label(text=f"Y: {dims_cm[1]:.2f} cm")
            layout.label(text=f"Z: {dims_cm[2]:.2f} cm")
        else:
            layout.label(text="No mesh selected")

        layout.separator()
        layout.prop(context.scene, "rcm_target_cm")
        layout.operator("rcm.scale_to_cm", icon='FULLSCREEN_ENTER')


# ----- REGISTER -----
classes = (RCM_OT_SetUnits, RCM_OT_ScaleToCM, RCM_PT_Panel)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rcm_target_cm = bpy.props.FloatProperty(
        name="Target cm",
        default=100.0,
        min=0.001,
        description="Target maximum dimension in centimeters"
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.rcm_target_cm

if __name__ == "__main__":
    register()

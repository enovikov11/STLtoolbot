import bpy

bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 0.001

font_path = bpy.path.abspath("//RobotoMono-Bold.ttf")
custom_font = bpy.data.fonts.load(font_path)

text = "хорни"

bpy.ops.object.text_add()
text_object = bpy.context.object
text_object.data.size = 15
text_object.data.body = text
text_object.data.extrude = 0.5
text_object.data.font = custom_font
bpy.ops.object.convert(target="MESH")

cover_size = 1
size_z = 1

text_x, text_y, text_z = zip(*text_object.bound_box)
cube_x = (min(text_x) + max(text_x)) / 2
cube_y = (min(text_y) + max(text_y)) / 2
cube_z = max(text_z) + size_z / 2 - 0.001

bpy.ops.mesh.primitive_cube_add(size=1, location=(cube_x, cube_y, cube_z))
cube = bpy.context.object
cube.scale.x = (max(text_x) - min(text_x)) + 2 * cover_size
cube.scale.y = (max(text_y) - min(text_y)) + 2 * cover_size
cube.scale.z = size_z

cone_depth = 6
cone_z = cube_z + size_z / 2 + cone_depth / 2 - 0.001
bpy.ops.mesh.primitive_cone_add(
    vertices=64, radius1=2, radius2=3, depth=cone_depth, location=(cube_x, cube_y, cone_z))

bpy.context.view_layer.update()
bpy.ops.object.select_all()
bpy.ops.export_mesh.stl(filepath="./text.stl")

from jsonrpc import JSONRPCResponseManager, dispatcher
import socket
import bpy
import os

global custom_font


@dispatcher.add_method
def init(ttf_path):
    global custom_font

    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 0.001

    font_path = bpy.path.abspath(ttf_path)
    custom_font = bpy.data.fonts.load(font_path)


@dispatcher.add_method
def build_text(text, path):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    bpy.ops.object.text_add()
    text_object = bpy.context.object
    text_object.data.size = 15
    text_object.data.body = text
    text_object.data.extrude = 0.5
    text_object.data.font = custom_font
    text_object.data.align_x = 'CENTER'
    text_object.data.align_y = 'CENTER'
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
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_mesh.stl(filepath=path, check_existing=False)


@dispatcher.add_method
def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


@dispatcher.add_method
def load(path):
    bpy.ops.import_mesh.stl(filepath=path)
    return bpy.context.object


@dispatcher.add_method
def cube(x1, x2, y1, y2, z1, z2):
    center = ((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2)
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)

    cube = bpy.context.object
    cube.scale.x = abs(x2 - x1)
    cube.scale.y = abs(y2 - y1)
    cube.scale.z = abs(z2 - z1)

    return cube


@dispatcher.add_method
def make_mold(obj, cover=5):
    x, y, z = zip(*obj.bound_box)
    assert min(x) < 0
    assert max(x) > 0
    x1, x2 = min(x) - cover, max(x) + cover
    y1, y2 = min(y) - cover, max(y) + cover
    z1, z2 = min(z) - cover, max(z) + cover

    return cube(x1, 0, y1, y2, z1, z2), cube(0, x2, y1, y2, z1, z2)


def start_rpc(path):
    if os.path.exists(path):
        os.remove(path)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(path)
    server.listen(1)

    connection, _ = server.accept()

    while True:
        data = connection.recv(16384)
        if not data:
            break
        print(data)

        response = JSONRPCResponseManager.handle(data, dispatcher)
        connection.sendall(response.json.encode())


if __name__ == "__main__":
    start_rpc("./jsonrpc.sock")

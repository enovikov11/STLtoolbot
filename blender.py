from telegram.ext import Application, MessageHandler, filters
from telegram import InputFile
import json
import bpy
import os
import re


def build(text, path):
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
    bpy.ops.object.delete()


async def on_text(update, context):
    if os.getenv("VERBOSE") == "1":
        print(json.dumps(update.to_dict()))

    if re.match(valid_text_re, update.message.text):
        build(update.message.text, "./temp.stl")
        with open("./temp.stl", "rb") as file:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=InputFile(file, update.message.text + ".stl"))
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Связь с автором - @enovikov11. Текст не прошел валидацию регуляркой " +
            str(valid_text_re)
        )

valid_text_re = r"^[ \nа-яёА-ЯЁa-zA-Z0-9!@#$%^&*()_+\-=\[\]{}|\\;:\"\',.<>\/?]{1,300}$"

bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 0.001
font_path = bpy.path.abspath("//RobotoMono-Bold.ttf")
custom_font = bpy.data.fonts.load(font_path)
bpy.ops.object.delete()

app = Application.builder().token(os.getenv("API_KEY")).build()
app.add_handler(MessageHandler(filters.TEXT, on_text))
app.run_polling()

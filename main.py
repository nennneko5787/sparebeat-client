from ursina import Entity, Sky, Ursina, camera, color
from ursina.shaders import unlit_shader

app = Ursina(title="sparebeat")

angle = 52
linePadding = 10.35

sky = Sky(
    parent=camera,
    name="sky",
    model="sky_dome",
    texture="assets/images/polygon",
    scale=9900,
    shader=unlit_shader,
    unlit=True,
    color=color.rgb32(100, 100, 100),
)

camera.fov = 90

leftLine = Entity(
    model="cube",
    color=color.rgb32(158, 206, 206),
    position=(linePadding, 0, 0),
    rotation=(angle, 0, 0),
    origin=(0, 0),
    scale=(0, 200, 1),
    collider="box",
)

rightLine = Entity(
    model="cube",
    color=color.rgb32(158, 206, 206),
    position=(-linePadding, 0, 0),
    rotation=(angle, 0, 0),
    origin=(0, 0),
    scale=(0, 200, 1),
    collider="box",
)


lane = Entity(
    model="cube",
    color=color.black,
    position=(0, -4, 0),
    rotation=(angle, 0, 0),
    origin=(0, 0),
    scale=(25, 200, 0),
    collider="box",
)


app.run()

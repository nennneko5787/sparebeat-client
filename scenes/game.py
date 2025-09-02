from ursina import Entity, Sky, camera, color, destroy
from ursina.shaders import unlit_shader


class GameScene(Entity):
    def __init__(self):
        super().__init__()
        angle = 52
        linePadding = 25 / 2

        self.sky = Sky(
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

        self.leftLine = Entity(
            model="cube",
            color=color.rgb32(158, 206, 206),
            position=(linePadding, -6, 0),
            rotation=(angle, 0, 0),
            origin=(0, 0),
            scale=(0, 200, 2),
            collider="box",
        )

        self.rightLine = Entity(
            model="cube",
            color=color.rgb32(158, 206, 206),
            position=(-linePadding, -6, 0),
            rotation=(angle, 0, 0),
            origin=(0, 0),
            scale=(0, 200, 2),
            collider="box",
        )

        self.lane = Entity(
            model="cube",
            color=color.black,
            position=(0, -6, 0),
            rotation=(angle, 0, 0),
            origin=(0, 0),
            scale=(25, 200, 0),
            collider="box",
        )

    def unload(self):
        destroy(self.sky)
        destroy(self.leftLine)
        destroy(self.rightLine)
        destroy(self.lane)

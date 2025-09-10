from ursina import *
from panda3d.core import *
from ursina.shaders.text_shader import text_shader


class Text3D(Entity):
    def __init__(
        self, text="", font: FontPool = None, color=color.white, scale=0.1, **kwargs
    ):
        super().__init__(**kwargs)
        self.font = font
        self.scale = scale
        self.color = color

        self.shader = text_shader
        self.shader.compile()

        self.tn = TextNode("text3d")
        self.tn.setText(text)

        if self.font:
            self.tn.setFont(self.font)

        self.tn.setAlign(TextNode.A_center)
        self.tn.setTextColor(self.color)

        self.node = self.attach_new_node(self.tn)
        self.node.set_scale(self.scale)
        self.node.setShader(self.shader._shader)

    def setText(self, text: str):
        self.node.remove_node()

        self.tn = TextNode("text3d")
        self.tn.setText(text)

        if self.font:
            self.tn.setFont(self.font)

        self.tn.setAlign(TextNode.A_center)
        self.tn.setTextColor(self.color)

        self.node = self.attach_new_node(self.tn)
        self.node.set_scale(self.scale)
        self.node.setShader(self.shader._shader)

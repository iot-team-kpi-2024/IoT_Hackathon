from kivy.app import App
from kivy.uix.image import Image
from kivy.graphics import Rotate
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty

class WindArrow(Image):
    rotation_angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super(WindArrow, self).__init__(**kwargs)
        self.bind(rotation_angle=self.update_rotation)

    def update_rotation(self, instance, value):
        # Clear existing canvas instructions
        self.canvas.before.clear()
        
        # Apply new rotation
        with self.canvas.before:
            # The rotation is centered around the middle of the image
            Rotate(angle=self.rotation_angle, origin=self.center)
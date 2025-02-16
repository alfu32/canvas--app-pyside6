from PySide6.QtCore import QPointF

from Drawable import Drawable, BoxDrawable, LinkDrawable


class ModelDrawable(Drawable):
    def __init__(self):
        self.drawables = []
        # Optionally store metamodel data for each box.
        self.metamodel = {}

    def add_drawable(self, drawable: Drawable):
        self.drawables.append(drawable)
        # If it's a box, store its metadata.
        if isinstance(drawable, BoxDrawable):
            self.metamodel[id(drawable)] = drawable.metadata
        if isinstance(drawable, LinkDrawable):
            self.metamodel[id(drawable)] = drawable.metadata
            drawable.box1.links.append(drawable)
            drawable.box2.links.append(drawable)

    def contains(self, point: QPointF) -> bool:
        for d in self.drawables:
            if d.contains(point):
                return True
        return False
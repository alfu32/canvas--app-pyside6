from typing import List

from PySide6.QtCore import QPointF

from Drawable import Drawable, BoxDrawable, LinkDrawable


class ModelDrawable(Drawable):

    feedbackDrawables:List[Drawable] = []

    def __init__(self):
        self.drawables = []
        # Optionally store metamodel data for each box.
        self.metamodel = {}
        self.feedbackDrawables=[]

    def add_drawable(self, drawable: Drawable):
        self.drawables.append(drawable)
        # If it's a box, store its metadata.
        if isinstance(drawable, BoxDrawable):
            self.metamodel[id(drawable)] = drawable.metadata
        if isinstance(drawable, LinkDrawable):
            self.metamodel[id(drawable)] = drawable.metadata
            drawable.box1.add_link(drawable)
            drawable.box2.add_link(drawable)

    def contains(self, point: QPointF) -> bool:
        for d in self.drawables:
            if d.contains(point):
                return True
        return False
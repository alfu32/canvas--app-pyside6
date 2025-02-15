from Drawable import Drawable, BoxDrawable


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

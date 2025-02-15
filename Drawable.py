from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPen, QColor


class Drawable:
    def draw(self, painter: QPainter, model, canvas):
        raise NotImplementedError

    def contains(self, point: QPointF) -> bool:
        raise NotImplementedError

    @staticmethod
    def build(inputs: list)  -> (list,'Drawable'):
        raise NotImplementedError


class BoxDrawable(Drawable):
    def __init__(self, rect: QRectF, metadata: dict):
        self.rect = rect
        self.metadata = metadata

    def draw(self, painter, model, canvas):
        pen = QPen(QColor("black"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(self.rect)
        # Optionally draw the box name.
        painter.drawText(self.rect, Qt.AlignLeft & Qt.AlignTop, self.metadata.get("name", ""))
        pass

    def contains(self, point: QPointF) -> bool:
        return self.rect.contains(point)

    @staticmethod
    def build(_inputs: list) -> (list,Drawable):
        """
        Expects: [point1 (QPointF), point2 (QPointF), text (str)]
        Returns: ([], boxDrawable) when complete, otherwise (list_of_error_messages, None)
        """
        # defaults
        final_inputs=[QPointF(0.0,0.0),"Box"]
        # validation : first matching QPoint and first matching string
        inputs=[next((x for x in _inputs if isinstance(x,QPointF)), final_inputs[0]),next((x for x in _inputs if isinstance(x,str)), None)]

        rect = QRectF(inputs[0], inputs[0] + QPointF(150.0,50.0)).normalized()
        box = BoxDrawable(rect, {"name": inputs[1]})
        if len(_inputs) == 0:
            return ["pick the box anchor Point."], box
        if len(_inputs) == 1:
            if isinstance(inputs[0],QPointF):
                box.rect=QRectF(inputs[0], inputs[0] + QPointF(150.0,50.0)).normalized()
                return ["start typing the box name then hit ENTER."], box
            else:
                return [f"input[0] was {input[0]}"], box
        elif len(_inputs) >= 2:
            rect = QRectF(inputs[0], inputs[0] + QPointF(150.0,50.0)).normalized()
            box.rect = rect
            box.metadata["name"] = inputs[1] if isinstance(inputs[1],str) else final_inputs[1]
            return [] if inputs[1] is not None else ["enter the box name"], box


    def __str__(self):
        return f"""Box:{{position:[{self.rect.bottomLeft().x():.02f},{self.rect.bottomLeft().y():.02f}],name:{self.metadata["name"]} }}"""


class LinkDrawable(Drawable):
    def __init__(self, box1: BoxDrawable, box2: BoxDrawable):
        self.box1 = box1
        self.box2 = box2

    def draw(self, painter: QPainter, model, canvas):
        pen = QPen(QColor("blue"))
        pen.setWidth(2)
        painter.setPen(pen)
        p1 = self.box1.rect.center()
        p2 = self.box2.rect.center()
        painter.drawLine(p1, p2)

    def contains(self, point: QPointF) -> bool:
        # For simplicity, we return False for link hit testing.
        return False

    @staticmethod
    def build(inputs: list) -> (list,Drawable):
        """
        Expects: [box1 (BoxDrawable), box2 (BoxDrawable), link_name (str)]
        Returns: ([], linkDrawable) when complete, otherwise (list_of_error_messages, None)
        """
        if len(inputs) == 0:
            return (["Pick the source box"], None)
        elif len(inputs) == 1:
            return (["Pick the destination box"], None)
        elif len(inputs) == 2:
            return (["Start typing the name of the box and then finish with ENTER"], None)
        box1, box2, link_name = inputs[0], inputs[1], inputs[2]
        if not (isinstance(box1, BoxDrawable) and isinstance(box2, BoxDrawable)):
            return (["First two inputs must be BoxDrawable instances."], None)
        if box1 == box2:
            return (["Boxes must be different."], None)
        link = LinkDrawable(box1, box2, {"name": link_name})
        return ([], link)

    def __str__(self):
        return f"""Link:{{source:{self.box1},target:{self.box2} }}"""

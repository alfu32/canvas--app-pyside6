import uuid

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPen, QColor

from events import CanvasKeyEvent, CanvasPointerEvent


class Drawable:
    id:str
    name:str
    metadata:dict

    def __init__(self):
        self.id=uuid.uuid4().hex.__str__()
        self.name="DrawableName"
        self.metadata={}

    def draw(self, painter: QPainter, model, canvas):
        raise NotImplementedError

    def contains(self, point: QPointF) -> bool:
        raise NotImplementedError

    @staticmethod
    def build(inputs: list,model:'ModelDrawable')  -> (list,'Drawable'):
        raise NotImplementedError


class BoxDrawable(Drawable):
    def __init__(self, rect: QRectF, metadata: dict):
        super().__init__()
        self.name="BoxDrawable"
        self.rect = rect
        self.metadata = metadata

    def draw(self, painter, model, canvas):
        pen = QPen(QColor("black"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(self.rect)
        # Optionally draw the box name.
        painter.drawText(self.rect, Qt.AlignLeft & Qt.AlignTop, self.name)
        pass

    def contains(self, point: QPointF) -> bool:
        return self.rect.contains(point)

    @staticmethod
    def build(_inputs: list,model:'ModelDrawable') -> (list,Drawable):
        """
        Expects: [point1 (QPointF), point2 (QPointF), text (str)]
        Returns: ([], boxDrawable) when complete, otherwise (list_of_error_messages, None)
        """

        name_event:CanvasKeyEvent=next((x for x in _inputs if isinstance(x,CanvasKeyEvent)), None)
        anchor_event:CanvasPointerEvent=next((x for x in _inputs if isinstance(x,CanvasPointerEvent)), None)
        input_anchor=QPointF(0.0,0.0)
        input_name="Box"
        errors=[]

        if anchor_event is None:
            errors.append("Choose the Box Position")
            input_anchor=QPointF(0.0,0.0)
        else:
            input_anchor=anchor_event.modelPoint
        if name_event is None:
            errors.append("Choose the Box Name")
            input_name="Box"
        else:
            input_name=name_event.buffer

        rect = QRectF(input_anchor, input_anchor + QPointF(150.0,50.0)).normalized()
        box = BoxDrawable(rect, {})
        box.name=input_name
        return errors,box

        # rect = QRectF(input_anchor, input_anchor + QPointF(150.0, 50.0)).normalized()
        # box = BoxDrawable(rect, {})
        # box.name = input_name
        # if len(_inputs) == 0:
        #     return ["pick the box anchor Point."], box
        # if len(_inputs) == 1:
        #     if isinstance(inputs[0], QPointF):
        #         box.rect = QRectF(inputs[0], inputs[0] + QPointF(150.0, 50.0)).normalized()
        #         return ["start typing the box name then hit ENTER."], box
        #     else:
        #         return [f"input[0] was {input[0]}"], box
        # elif len(_inputs) >= 2:
        #     rect = QRectF(inputs[0], inputs[0] + QPointF(150.0, 50.0)).normalized()
        #     box.rect = rect
        #     box.name = inputs[1] if isinstance(inputs[1], str) else final_inputs[1]
        #     return [] if inputs[1] is not None else ["enter the box name"], box


    def __str__(self):
        return f"""Box:{{position:[{self.rect.bottomLeft().x():.02f},{self.rect.bottomLeft().y():.02f}],name:{self.name},id:{self.id} }}"""


class LinkDrawable(Drawable):
    def __init__(self, box1: BoxDrawable, box2: BoxDrawable,metadata:dict):
        super().__init__()
        self.name="link"
        self.box1 = box1
        self.box2 = box2
        self.metadata=metadata

    def draw(self, painter: QPainter, model, canvas):
        pen = QPen(QColor("blue"))
        pen.setWidth(2)
        painter.setPen(pen)
        p1 = self.box1.rect.topRight()
        p2 = self.box2.rect.bottomLeft()
        painter.drawLine(p1, p2)

    def contains(self, point: QPointF) -> bool:
        # For simplicity, we return False for link hit testing.
        return False

    @staticmethod
    def build(inputs: list,model:'ModelDrawable') -> (list,Drawable):
        """
        Expects: [box1 (BoxDrawable), box2 (BoxDrawable), link_name (str)]
        Returns: ([], linkDrawable) when complete, otherwise (list_of_error_messages, None)
        """
        name_event:CanvasKeyEvent=next((x for x in inputs if isinstance(x,CanvasKeyEvent)), None)
        anchor_events:list[CanvasPointerEvent]=[x for x in inputs if isinstance(x,CanvasPointerEvent)]
        box1 = anchor_events[0] if len(anchor_events) > 0 else BoxDrawable(QRectF(QPointF(0,0),QPointF(0,0)),model)
        box2 = anchor_events[1] if len(anchor_events) > 1 else box1
        input_name="link"

        errors=[]

        if len(anchor_events) == 0:
            errors.append("Choose the First Box")
        elif len(anchor_events) == 1:
            errors.append("Choose the Second Box")
        if name_event is None:
            errors.append("Choose the Box Name")
            input_name="link"
        else:
            input_name=name_event.buffer

        link = LinkDrawable(box1, box2, {})
        link.name=input_name
        return errors,link

        # matches = [x for x in inputs if isinstance(x,CanvasPointerEvent) and model.contains(x)]
        # point1 = matches[0] if len(matches) > 0 else None
        # point2 = matches[1] if len(matches) > 1 else point1
        # input_name:str=next((x for x in inputs if isinstance(x,str)), None)
        # errors=[]
        #
        # if len(matches) == 0:
        #     errors.append("Pick the first box")
        # if len(matches) == 1:
        #     errors.append("Pick the Second box")
        # if input_name is None:
        #     errors.append("Enter the link Name")
        #     input_name="link"
        #
        # under1 = next((d for d in model.drawables if point1 is not None and d.contains(point1)),None)
        # under2 = next((d for d in model.drawables if point2 is not None and d.contains(point2)),under1)
        # if under1 is not None and under2 is not None:
        #     link = LinkDrawable(under1, under2, {})
        #     link.name=input_name
        #     return errors,link
        # else:
        #     return errors,None

    def __str__(self):
        return f"""Link:{{source:{self.box1},target:{self.box2},name:{self.name},id:{self.id} }}"""

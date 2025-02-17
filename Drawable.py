
from __future__ import annotations
import uuid
from math import atan2

from PySide6.QtCore import QPointF, QRectF, Qt, QRect
from PySide6.QtGui import QPainter, QPen, QColor

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ModelDrawable import ModelDrawable

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
    def build(inputs: list,model:ModelDrawable)  -> (list,'Drawable'):
        raise NotImplementedError

class NullDrawable:
    id:str
    name:str
    metadata:dict

    def __init__(self):
        self.id=uuid.uuid4().hex.__str__()
        self.name="DrawableName"
        self.metadata={}

    def draw(self, painter: QPainter, model, canvas):
        pass

    def contains(self, point: QPointF) -> bool:
        return False

    @staticmethod
    def build(inputs: list,model:ModelDrawable)  -> (list,'Drawable'):
        return ["null drawable"],NullDrawable()


class SelectDrawable:
    id:str
    name:str
    metadata:dict
    rect:QRectF
    selection:list[Drawable] = []
    rtl:bool

    def __init__(self):
        self.id=uuid.uuid4().hex.__str__()
        self.name="DrawableName"
        self.metadata={}
        self.rect=QRectF()
        self.selection=[]
        self.rtl=True

    def draw(self, painter: QPainter, model, canvas):
        pen = QPen(QColor(0x00,0x88,0x88,0xff))
        pen.setWidth(1)
        if not self.rtl:
            pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.fillRect(self.rect,QColor(0x00,0xcc,0xcc,0x3f))
        painter.drawRect(self.rect)
        # Optionally draw the box name.
        # painter.drawText(self.rect.topLeft() + QPointF(5,15), self.name)

    def contains(self, point: QPointF) -> bool:
        return False

    @staticmethod
    def build(inputs: list,model:ModelDrawable)  -> (list,'Drawable'):
        box = SelectDrawable()

        points:list[CanvasPointerEvent]=[x for x in inputs if isinstance(x,CanvasPointerEvent)]
        errors=[]
        start = QPointF(0.0, 0.0)
        end = QPointF(0.0, 0.0)
        box.rect = QRectF(start,end).normalized()
        box.selection=[]
        keys:list[CanvasKeyEvent]=[x for x in inputs if isinstance(x,CanvasKeyEvent)]
        print(len(inputs))
        if Qt.Key_Escape in keys:
            while len(inputs) > 0:
                inputs.pop(0)
                model.selection=[]

        if len(points) == 0:
            errors.append("select start point")
        elif len(points) % 2 == 1:
            errors.append("select end point")
            points=points[-1:]
            start=points[0].modelPoint
            end=start
            box.rect = QRectF(start,end).normalized()
            box.selection=[]
        elif len(points) % 2 == 0:
            errors.append("selection window ready")
            points=points[-2:]
            start=points[0].modelPoint
            end=points[1].modelPoint
            box.rect = QRectF(start,end).normalized()
            box.rtl=start.x() < end.x()
            box.selection=model.find_drawables_inside(box.rect) if start.x() < end.x() else model.find_drawables_crossing(box.rect)
            model.selection.extend(box.selection)

        model.feedbackDrawables=[box]

        return errors,box

class BoxDrawable(Drawable):
    links:list['LinkDrawable'] = []

    def __init__(self, rect: QRectF, metadata: dict):
        super().__init__()
        self.name="BoxDrawable"
        self.rect = rect
        self.metadata = metadata

    def get_rect(self) -> QRectF:
        supYCount = max(
            len([l for l in self.links if l.box1 == self]),
            len([l for l in self.links if l.box2 == self]),
        )
        return QRectF(self.rect.topLeft(), self.rect.bottomRight() + QPointF(0,supYCount*15.0))


    def add_link(self,link:'LinkDrawable'):
        self.links.append(link)
        self.links.sort(lambda l: l.get_direction())

    def draw(self, painter, model, canvas):
        pen = QPen(QColor("black"))
        pen.setWidth(2)
        painter.setPen(pen)
        r=self.get_rect()
        painter.drawRect(r)
        # Optionally draw the box name.
        painter.drawText(self.rect.topLeft() + QPointF(5,15), self.name)
        pass

    def contains(self, point: QPointF) -> bool:
        return self.get_rect().contains(point)

    @staticmethod
    def build(_inputs: list,model:ModelDrawable) -> (list,Drawable):
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

    def copy(self) -> 'BoxDrawable':
        return BoxDrawable(
            rect=self.rect.__copy__(),
            metadata=self.metadata
        )

    def __str__(self):
        return f"""Box:{{position:[{self.rect.bottomLeft().x():.02f},{self.rect.bottomLeft().y():.02f}],name:{self.name},id:{self.id} }}"""

    def get_outgoing_order(self, link:'LinkDrawable') -> int:
        try:
            links:list[LinkDrawable] = [x for x in self.links if x.box1 == self]
            links.sort(key=lambda l: l.get_direction())
            index = links.index(link)
            # print("Index:", index)
            return index
        except ValueError:
            # print("Element not found in the list.")
            return 0

    def get_incoming_order(self, link:'LinkDrawable') -> int:
        try:
            links = [x for x in self.links if x.box2 == self]
            links.sort(key=lambda l: l.get_direction(),reverse=True)
            index = links.index(link)
            # print("Index:", index)
            return index
        except ValueError:
            # print("Element not found in the list.")
            return 0


class LinkDrawable(Drawable):
    def __init__(self, box1: BoxDrawable, box2: BoxDrawable,metadata:dict):
        super().__init__()
        self.name="link"
        self.box1 = box1
        self.box2 = box2
        self.metadata=metadata

    def get_direction(self) -> float:
        p1 = self.box1.rect.topRight() + QPointF(0,25) #  + QPointF(0,25 + self.box1.get_outgoing_order(self) * 5 )
        p2 = self.box2.rect.topLeft() + QPointF(0,25)  # + QPointF(0,25 + self.box2.get_incoming_order(self) * 5 )

        delta = p2 - p1 - QPointF(100,0)
        return atan2(delta.y(),delta.x())

    def draw(self, painter: QPainter, model, canvas):
        pen = QPen(QColor("blue"))
        pen.setWidth(2)
        painter.setPen(pen)
        p1 = self.box1.rect.topRight() + QPointF(0,25 + self.box1.get_outgoing_order(self) * 15 )
        p2 = self.box2.rect.topLeft() + QPointF(0,25 + self.box2.get_incoming_order(self) * 15 )

        painter.drawLine(p1, p1+QPointF(50,0))
        painter.drawLine(p1+QPointF(50,0), p2-QPointF(50,0))
        painter.drawLine(p2-QPointF(50,0), p2)

        # Define offsets for the text labels so they don't overlap the line.
        offset_start = QPointF(5, -2)  # Adjust as needed for the start label.
        offset_end = QPointF(-55, -2)  # Adjust as needed for the end label.

        # Draw text at the start and end of the segment.
        painter.drawText(p1 + offset_start, self.name)
        painter.drawText(p2 + offset_end, self.name)

    def contains(self, point: QPointF) -> bool:
        # For simplicity, we return False for link hit testing.
        return False

    @staticmethod
    def build(inputs: list,model:ModelDrawable) -> (list,Drawable):
        """
        Expects: [box1 (BoxDrawable), box2 (BoxDrawable), link_name (str)]
        Returns: ([], linkDrawable) when complete, otherwise (list_of_error_messages, None)
        """
        name_event:CanvasKeyEvent=next((x for x in inputs if isinstance(x,CanvasKeyEvent)), None)
        anchor_events:list[CanvasPointerEvent]=[x for x in inputs if isinstance(x,CanvasPointerEvent)]
        m0=anchor_events[0].modelPoint if len(anchor_events)>0 else QPointF(0,0)
        t0=anchor_events[0].target if len(anchor_events)>0 else None
        m1=anchor_events[1].modelPoint if len(anchor_events)>1 else m0
        t1=anchor_events[1].target if len(anchor_events)>1 else None
        box1 = t0 if t0 is not None else BoxDrawable(QRectF(m0,m0 + QPointF(1,1)),model)
        box2 = t1 if t1 is not None else BoxDrawable(QRectF(m1,m1 + QPointF(1,1)),model)

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

    def __str__(self):
        return f"""Link:{{source:{self.box1},target:{self.box2},name:{self.name},id:{self.id} }}"""

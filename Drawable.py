from __future__ import annotations

import json
import uuid
from functools import reduce
from math import atan2

from PySide6.QtCore import QPointF, QRectF, Qt, QRect, QObject, QPoint, QMarginsF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ModelDrawable import ModelDrawable

from events import CanvasKeyEvent, CanvasPointerEvent




class Drawable:
    id: str
    name: str
    metadata: dict
    is_finalized: bool
    children: list['Drawable']
    links: list['LinkDrawable'] = []
    rect:QRectF

    def __init__(self):
        self.id = uuid.uuid4().hex.__str__()
        self.name = "DrawableName"
        self.metadata = {}
        self.is_finalized = False
        self.children=[]
        self.rect = QRectF()

    def get_rect(self) -> QRectF:
        calcY = max(
            len([l for l in self.links if l.box1 == self]) * 15.0,
            len([l for l in self.links if l.box2 == self]) * 15.0,
        )
        cr=QRectF(self.rect.topLeft(), self.rect.bottomRight() + QPointF(0, calcY))
        if len(self.children) > 0:
            rect = cr
            for child in self.children:
                rect=rect.united(child.get_rect())
            return rect
        else:
            return cr

    def draw(self, painter: QPainter, model:ModelDrawable,canvas:'CanvasQWidget'):
        for cd in self.children:
            cd.draw(painter, model, canvas)

    def get_hotspots(self) -> list['HotSpot']:
        # hotspots = []
        # for child in self.children:
        #     for hs in child.get_hotspots():
        #         hotspots.append(hs)
        # return hotspots
        return []

    def contains(self, point: QPointF) -> bool:
        for child in self.children:
            if child.contains(point):
                return True
        return False


    def find_drawables_inside(self, rect: QRectF) -> List[Drawable]:
        """
        Finds all drawables that are **completely contained** within the given rectangle.
        """
        result = []
        if rect.contains(self.get_rect()) or len(self.get_hotspots()) == len(
                [hs for hs in self.get_hotspots() if rect.contains(hs.point)]):
            result.append(self)
        for child in self.children:
            rest = child.find_drawables_inside(rect)
            for ch in rest:
                result.append(ch)
        return result

    def find_drawables_crossing(self, rect: QRectF) -> List[Drawable]:
        """
        Finds all drawables that **partially overlap** (intersect) with the given rectangle.
        """
        result = []
        if rect.intersects(self.get_rect()) or rect.contains(self.get_rect()) or [hs for hs in self.get_hotspots() if rect.contains(hs.point)]:
            result.append(self)
        for child in self.children:
            rest = child.find_drawables_crossing(rect)
            for ch in rest:
                result.append(ch)
        return result

    @staticmethod
    def build(inputs: list, model: ModelDrawable) -> (list, 'Drawable'):
        raise NotImplementedError

    def add_child(self,child:'Drawable'):
        self.children.append(child)

    def remove_child(self,child:'Drawable'):
        self.children.remove(child)

class HotSpot(Drawable):

    def __init__(self, point: QPointF, parent: Drawable, onclick):
        super().__init__()
        self.point = point
        self.onclick = onclick
        self.parent = parent

    def draw(self,painter: QPainter, model:ModelDrawable,canvas:'CanvasQWidget'):
        """
        Draws a hotspot marker at the given QPointF using a QPainter.

        - Draws a small filled circle at the point.
        - Optionally, draws a cross for better visibility.
        """
        if not painter:
            return

        radius = 5  # Size of the hotspot
        fill = QColor(0, 0, 0)  # Red color for visibility
        fill.setHsv(240, 127, 127, 100)
        line = QColor(0, 0, 0)  # Red color for visibility
        line.setHsv(240, 127, 127, 255)

        # Save painter state
        painter.save()

        # Set brush and pen
        painter.setBrush(QBrush(fill, Qt.SolidPattern))  # 1 = Qt.SolidPattern (for full transparency effect)
        painter.setPen(line)  # Border color

        # Optional: Draw a cross (for better visibility)
        cross_size = 10.0
        x = int(self.point.x())
        y = int(self.point.y())
        re = QRect(QPoint(x - radius, y - radius), QPoint(x + radius, y + radius), )
        painter.drawRect(re)
        painter.fillRect(re, fill)

        # Restore painter state
        painter.restore()

    def contains(self, point: QPointF) -> bool:
        d = self.point - point
        x=d.x()
        y=d.y()
        return (x*x + y*y) < 25

class NullDrawable:

    def __init__(self):
        super().__init__()

    def get_rect(self) -> QRectF:
        return QRectF()

    def draw(self, painter: QPainter, model, canvas):
        pass

    def contains(self, point: QPointF) -> bool:
        return False

    def get_hotspots(self) -> list[QPointF]:
        return []

    @staticmethod
    def build(inputs: list, model: ModelDrawable) -> (list, 'Drawable'):
        return ["null drawable"], NullDrawable()


class SelectDrawable:
    selection: list[Drawable] = []
    rtl: bool

    def __init__(self):
        super().__init__()
        self.selection = []
        self.rtl = True

    def get_rect(self) -> QRectF:
        return QRectF(self.rect.topLeft(), self.rect.bottomRight())

    def draw(self, painter: QPainter, model, canvas):
        pen = QPen(QColor(0x00, 0x88, 0x88, 0xff))
        pen.setWidth(1)
        if not self.rtl:
            pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.fillRect(self.rect, QColor(0x00, 0xcc, 0xcc, 0x3f))
        painter.drawRect(self.rect)
        # Optionally draw the box name.
        # painter.drawText(self.rect.topLeft() + QPointF(5,15), self.name)

    def get_hotspots(self) -> list[HotSpot]:
        all = []
        for selected in self.selection:
            hotspots = selected.get_hotspots()
            for hotspot in hotspots:
                all.append(hotspot)
        return all

    def hotspot_click(self,x:CanvasPointerEvent):
        if self.move_reference is None and x.type == 'pointerdown':
            print(f"started moving {x}")
            self.move_reference = x.modelPoint
            #self.rect.moveTo(x.modelPoint)
        elif self.move_reference is not None and x.type == 'pointerup':
            print(f"finished moving {x}")
            self.move_reference = None

    def contains(self, point: QPointF) -> bool:
        return False

    @staticmethod
    def build(inputs: list, model: ModelDrawable) -> (list, 'Drawable'):
        box = SelectDrawable()

        points: list[CanvasPointerEvent] = [x for x in inputs if isinstance(x, CanvasPointerEvent)]
        errors = []
        start = QPointF(0.0, 0.0)
        end = QPointF(0.0, 0.0)
        box.rect = QRectF(start, end).normalized()
        box.selection = []
        keys: list[CanvasKeyEvent] = [x for x in inputs if isinstance(x, CanvasKeyEvent)]
        # print(len(inputs))
        if Qt.Key_Escape in keys:
            while len(inputs) > 0:
                inputs.pop(0)
                model.selection = []

        if len(points) == 0:
            errors.append("select start point")
        elif len(points) % 2 == 1:
            errors.append("select end point")
            points = points[-1:]
            start = points[0].modelPoint
            end = start
            box.rect = QRectF(start, end).normalized()
        elif len(points) % 2 == 0:
            points = points[-2:]
            start = points[0].modelPoint
            end = points[1].modelPoint
            box.rect = QRectF(start, end).normalized()
            box.rtl = start.x() < end.x()

        model.feedbackDrawables = [box]

        return errors, box


class BoxDrawable(Drawable):
    move_reference:QPointF = None

    def __init__(self, rect: QRectF, metadata: dict):
        super().__init__()
        self.rect = rect
        self.metadata = metadata

    def get_rect(self) -> QRectF:
        calcY = max(
            len([l for l in self.links if l.box1 == self]) * 15.0,
            len([l for l in self.links if l.box2 == self]) * 15.0,
        )
        cr=QRectF(self.rect.topLeft(), self.rect.bottomRight() + QPointF(0, calcY))
        if len(self.children) > 0:
            cr=super().get_rect().marginsAdded(QMarginsF(50.0,50.0,100.0,100.0))
            calcY = max(calcY,cr.height())
            cr.setHeight(calcY)
            return cr
        else:
            return QRectF(self.rect.topLeft(), self.rect.bottomRight() + QPointF(0, calcY))

    def get_hotspots(self) -> list[HotSpot]:
        rect = self.get_rect()
        return [
            HotSpot(rect.topLeft(),self,None ),
            HotSpot(rect.topRight(),self, None ),
            HotSpot(rect.bottomRight(),self, None ),
            HotSpot(rect.bottomLeft(),self, None ),
        ]

    def add_link(self, link: 'LinkDrawable'):
        if link.id not in [l.id for l in self.links]:
            self.links.append(link)
            self.links.sort(key=lambda l: l.get_direction())

    def draw(self, painter, model, canvas):
        pen = QPen(QColor("black"))
        pen.setWidth(2)
        painter.setPen(pen)
        r = self.get_rect()
        painter.drawRect(r)
        # Optionally draw the box name.
        painter.drawText(r.topLeft() + QPointF(5, 15), self.name)
        # left=1
        # right=1
        # for lnk in self.links:
        #     tl = r.topLeft()
        #     tr = r.topRight()
        #     if lnk.box1 == self:
        #         painter.drawText(tl + QPointF(5, 15*left), lnk.name)
        #         left+=1
        #     elif lnk.box2 == self:
        #         painter.drawText(tr + QPointF(5, 15*right), lnk.name)
        #         right+=1
        #     else:
        #         painter.drawText( tr + QPointF(50, 15 * right), lnk.name)
        super().draw(painter, model, canvas)
        pass

    def contains(self, point: QPointF) -> bool:
        return self.get_rect().contains(point)

    @staticmethod
    def build(_inputs: list, model: ModelDrawable) -> (list, Drawable):
        """
        Expects: [point1 (QPointF), point2 (QPointF), text (str)]
        Returns: ([], boxDrawable) when complete, otherwise (list_of_error_messages, None)
        """

        name_event: CanvasKeyEvent = next((x for x in _inputs if isinstance(x, CanvasKeyEvent)), None)
        anchor_event: CanvasPointerEvent = next((x for x in _inputs if isinstance(x, CanvasPointerEvent)), None)
        input_anchor = QPointF(0.0, 0.0)
        input_name = "Box"
        errors = []

        if anchor_event is None:
            errors.append("Choose the Box Position")
            input_anchor = QPointF(0.0, 0.0)
        else:
            input_anchor = anchor_event.modelPoint
        if name_event is None:
            errors.append("Choose the Box Name")
            input_name = "Box"
        else:
            input_name = name_event.buffer

        rect = QRectF(input_anchor, input_anchor + QPointF(150.0, 50.0)).normalized()
        box = BoxDrawable(rect, {})
        box.name = input_name
        return errors, box

    def copy(self) -> 'BoxDrawable':
        return BoxDrawable(
            rect=self.rect.__copy__(),
            metadata=self.metadata
        )

    def __str__(self):
        return f"""Box:{{position:[{self.rect.bottomLeft().x():.02f},{self.rect.bottomLeft().y():.02f}],name:{self.name},id:{self.id} }}"""

    def get_outgoing_order(self, link: 'LinkDrawable') -> int:
        try:
            links: list[LinkDrawable] = [x for x in self.links if x.box1 == self]
            links.sort(key=lambda l: l.get_direction())
            index = links.index(link)
            # print("Index:", index)
            return index
        except ValueError:
            # print("Element not found in the list.")
            return 0

    def get_incoming_order(self, link: 'LinkDrawable') -> int:
        try:
            links = [x for x in self.links if x.box2 == self]
            links.sort(key=lambda l: l.get_direction(), reverse=True)
            index = links.index(link)
            # print("Index:", index)
            return index
        except ValueError:
            # print("Element not found in the list.")
            return 0


class LinkDrawable(Drawable):
    move_reference:QPointF

    def __init__(self, box1: BoxDrawable, box2: BoxDrawable, metadata: dict):
        super().__init__()
        self.name = "link"
        self.box1 = box1
        self.box2 = box2
        self.metadata = metadata

    def get_direction(self) -> float:
        p1 = self.box1.rect.topRight() + QPointF(0, 25)  #  + QPointF(0,25 + self.box1.get_outgoing_order(self) * 5 )
        p2 = self.box2.rect.topLeft() + QPointF(0, 25)  # + QPointF(0,25 + self.box2.get_incoming_order(self) * 5 )

        delta = p2 - p1 - QPointF(100, 0)
        return atan2(delta.y(), delta.x())

    def draw(self, painter: QPainter, model, canvas):
        pen = QPen(QColor("blue"))
        pen.setWidth(2)
        painter.setPen(pen)
        p1 = self.box1.get_rect().topRight() + QPointF(0, 25 + self.box1.get_outgoing_order(self) * 15)
        p2 = self.box2.get_rect().topLeft() + QPointF(0, 25 + self.box2.get_incoming_order(self) * 15)

        painter.drawLine(p1, p1 + QPointF(50, 0))
        painter.drawLine(p1 + QPointF(50, 0), p2 - QPointF(50, 0))
        painter.drawLine(p2 - QPointF(50, 0), p2)

        # Define offsets for the text labels so they don't overlap the line.
        offset_start = QPointF(5, -2)  # Adjust as needed for the start label.
        offset_end = QPointF(-55, -2)  # Adjust as needed for the end label.

        # Draw text at the start and end of the segment.
        painter.drawText(p1 + offset_start, self.name)
        painter.drawText(p2 + offset_end, self.name)

    def get_hotspots(self) -> list[HotSpot]:
        return [
            HotSpot(self.box1.get_rect().topRight() + QPointF(0, 25 + self.box1.get_outgoing_order(self) * 15),self,None),
            HotSpot(self.box2.get_rect().topLeft() + QPointF(0, 25 + self.box2.get_incoming_order(self) * 15),self,None),
        ]

    def contains(self, point: QPointF) -> bool:
        # For simplicity, we return False for link hit testing.
        return False

    def get_rect(self):
        p1 = self.box1.get_rect().topRight() + QPointF(0, 25 + self.box1.get_outgoing_order(self) * 15)
        p2 = self.box2.get_rect().topLeft() + QPointF(0, 25 + self.box2.get_incoming_order(self) * 15)
        return QRectF(p1,p2).normalized()

    @staticmethod
    def build(inputs: list, model: ModelDrawable) -> (list, Drawable):
        """
        Expects: [box1 (BoxDrawable), box2 (BoxDrawable), link_name (str)]
        Returns: ([], linkDrawable) when complete, otherwise (list_of_error_messages, None)
        """
        name_event: CanvasKeyEvent = next((x for x in inputs if isinstance(x, CanvasKeyEvent)), None)
        anchor_events: list[CanvasPointerEvent] = [x for x in inputs if isinstance(x, CanvasPointerEvent)]
        m0 = anchor_events[0].modelPoint if len(anchor_events) > 0 else QPointF(0, 0)
        t0 = anchor_events[0].target if len(anchor_events) > 0 else None
        m1 = anchor_events[1].modelPoint if len(anchor_events) > 1 else m0
        t1 = anchor_events[1].target if len(anchor_events) > 1 else None
        box1 = t0 if t0 is not None else BoxDrawable(QRectF(m0, m0 + QPointF(1, 1)), model)
        box2 = t1 if t1 is not None else BoxDrawable(QRectF(m1, m1 + QPointF(1, 1)), model)

        errors = []

        if len(anchor_events) == 0:
            errors.append("Choose the First Box")
        elif len(anchor_events) == 1:
            errors.append("Choose the Second Box")

        if name_event is None:
            errors.append("Choose the Box Name")
            input_name = "link"
        else:
            input_name = name_event.buffer

        link = LinkDrawable(box1, box2, {})
        link.name = input_name
        return errors, link

    def __str__(self):
        return f"""Link:{{source:{self.box1},target:{self.box2},name:{self.name},id:{self.id} }}"""

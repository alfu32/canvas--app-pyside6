from typing import List

from PySide6.QtCore import Signal, QRectF, QPointF, QTimer, QRect, QPoint
from PySide6.QtGui import QPainter, QMouseEvent, QWheelEvent, QColor, Qt, QTransform, QFontDatabase, QFont, QBrush
from PySide6.QtWidgets import QWidget
from shiboken6.Shiboken import delete

from Drawable import Drawable
from ModelDrawable import ModelDrawable
from events import CanvasPointerEvent, CanvasZoomEvent, CanvasKeyEvent

class CanvasQWidget(QWidget):
    pointerDown = Signal(CanvasPointerEvent)  # (drawablesUnderPointer, viewport, screenPoint)
    pointerUp = Signal(CanvasPointerEvent)
    pointerMove = Signal(CanvasPointerEvent)  # (scale, centerPoint)
    zoomFinished = Signal(CanvasZoomEvent)  # (scale, centerPoint)
    bufferChanged = Signal(CanvasKeyEvent)  # (scale, centerPoint)
    bufferFinished = Signal(CanvasKeyEvent)  # (scale, centerPoint)
    # feedbackDrawables:List[Drawable] = []
    last_pointer_event:CanvasPointerEvent=None

    hotspot_event_start:CanvasPointerEvent=None
    hotspot_event_start_hostspot:'HotSpot'=None

    def __init__(self, parent=None):
        super().__init__(parent)
        font_path = "./Bahnschrift-Font-Family/BAHNSCHRIFT.TTF"
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.custom_font = QFont(family, 12)  # Use desired size.
        else:
            self.custom_font = QFont("Arial", 12)  # Fallback font.

        self.inputBuffer=""
        self.model = ModelDrawable()
        self.setMinimumSize(400, 400)
        # viewport parameters
        self.offset = QPointF(0, 0)
        self.scale = 1.0

        # For zoom finish detection.
        self._zoomTimer = QTimer(self)
        self._zoomTimer.setInterval(300)
        self._zoomTimer.setSingleShot(True)
        self._zoomTimer.timeout.connect(self._onZoomFinished)
        # Enable mouse tracking so we receive mouse move events even without button presses.
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def get_transform(self):
        """Returns the current transform matrix (model to screen)."""
        transform = QTransform()
        transform.translate(self.offset.x(), self.offset.y())
        transform.scale(self.scale, self.scale)
        return transform

    def model_to_screen(self, point: QPointF) -> QPointF:
        """
        Converts a point from model coordinates to screen coordinates.
        """
        transform = self.get_transform()
        return transform.map(point)

    def screen_to_model(self, point: QPointF) -> QPointF:
        """
        Converts a point from screen coordinates to model coordinates.
        """
        transform = self.get_transform()
        inv, invertible = transform.inverted()
        if invertible:
            return inv.map(point)
        else:
            # Should not happen if scale != 0.
            return point

    def paintEvent(self, event):
        # print("paintEvent triggered")  # Debug statement

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(self.custom_font)

        # Fill background with white.
        painter.fillRect(self.rect(), QColor("white"))
        # Apply transform.
        painter.translate(self.offset)
        painter.scale(self.scale, self.scale)

        # Draw each drawable from the model.
        painter.fillRect(self.get_transform().mapRect(self.rect()), QColor("white"))
        for drawable in self.model.drawables:
            drawable.draw(painter, self.model, self)
        for drawable in self.model.feedbackDrawables:
            drawable.draw(painter, self.model, self)
        for drawable in self.model.selection:
            for hs in drawable.get_hotspots():
                hs.draw(painter,self.model,self)
        painter.end()

    def get_target_boxes(self,modelPoint:QPointF,parent:Drawable=None) -> list[Drawable]:
        dwb=[]
        if parent is None:
            for d in self.model.drawables:
                if d.contains(modelPoint):
                    dwb.append(d)
                    rest = self.get_target_boxes(modelPoint,d)
                    for r in rest:
                        dwb.append(r)
        else:
            for d in parent.children:
                if d.contains(modelPoint):
                    dwb=[d]
                    rest = self.get_target_boxes(modelPoint,d)
                    for r in rest:
                        dwb.append(r)
        dwb.reverse()
        return dwb


    def get_canvas_pointer_event(self,event: QMouseEvent)->CanvasPointerEvent:
        screenPoint=event.position()
        modelPoint = self.screen_to_model(screenPoint)
        under = self.get_target_boxes(modelPoint)
        self.last_pointer_event =  CanvasPointerEvent(
            screenPoint=screenPoint,
            modelPoint=modelPoint,
            targetPath=under,
            target=under[0] if len(under)>0 else None,
            qevent=event,
            model=self.model
        )
        return self.last_pointer_event


    def mousePressEvent(self, event: QMouseEvent):
        cpe=self.get_canvas_pointer_event(event)
        cpe.type='pointerdown'
        if self.hotspot_event_start is None:
            self.pointerDown.emit(cpe)
            super().mousePressEvent(event)
        else:
            pass

    def mouseReleaseEvent(self, event: QMouseEvent):
        cpe=self.get_canvas_pointer_event(event)
        cpe.type='pointerup'
        for drawable in self.model.selection:
            for hs in drawable.get_hotspots():
                if hs.contains(cpe.modelPoint):
                    # hs.onclick(cpe)
                    if self.hotspot_event_start is None:
                        print(f"hotspot click started")
                        self.hotspot_event_start=cpe
                        self.hotspot_event_start_hostspot=hs
                        for sel in self.model.selection:
                            sel.anchor = sel.rect.topLeft()
                        return
        if self.hotspot_event_start is None:
            self.pointerUp.emit(cpe)
            super().mouseReleaseEvent(event)
        else:
            print(f"hotspot click ended")
            self.hotspot_event_start = None
            self.hotspot_event_start_hostspot = None
            for sel in self.model.selection:
                sel.anchor=None

    def mouseMoveEvent(self, event: QMouseEvent):
        cpe=self.get_canvas_pointer_event(event)
        cpe.type='pointermove'
        if self.hotspot_event_start is None:
            self.pointerMove.emit(cpe)
            super().mouseMoveEvent(event)
        else:
            hs:'HotSpot'=self.hotspot_event_start_hostspot
            print(hs.kind)
            # if hs.kind == "BoxDrawable.topLeft":
            delta = cpe.modelPoint - self.hotspot_event_start.modelPoint
            # print(f"hotspot action move {delta}")
            for sel in self.model.selection:
                new_topleft = sel.anchor + delta
                print(f"hotspot action move from {sel.rect.topLeft()} to {new_topleft}")
                sel.rect.moveTo(new_topleft)
            self.update()

    def wheelEvent(self, event: QWheelEvent):
        # Get the mouse pointer position (screen coordinates).
        pointer = QPointF(event.position())
        # Determine zoom factor.
        delta = event.angleDelta().y()
        zoomFactor = 1.0 + delta / 240.0  # adjust sensitivity as needed

        # Update scale.
        oldScale = self.scale
        self.scale *= zoomFactor

        # Adjust the offset so that the pointer remains fixed.
        # new_offset = pointer - zoomFactor * (pointer - old_offset)
        self.offset = pointer - (pointer - self.offset) * zoomFactor

        self.update()
        screenPoint=event.point(0).position()
        modelPoint = self.get_transform().map(screenPoint)
        under = self.get_target_boxes(modelPoint)


        self.zoomFinished.emit(CanvasZoomEvent(
            modelPoint=modelPoint,
            screenPoint=screenPoint,
            targetPath=under,
            target=under[0] if len(under)>0 else None,
            zoomValue=delta,
            transformMatrix=self.get_transform(),
            qevent=event,
            model=self.model
        ))
        self._zoomTimer.start()  # restart timer to detect zoom finish

    def keyReleaseEvent(self, event):
        key = event.key()
        # self.pointerMove.emit(self.last_pointer_event)
        if key in (Qt.Key_Return, Qt.Key_Enter):
            #print(f"Enter pressed. raising buffer '{self.inputBuffer}'.")
            self.bufferFinished.emit(CanvasKeyEvent(key=key,buffer=self.inputBuffer,qevent=event,model=self.model,isFinished=True))
            self.inputBuffer = ""
        elif key == Qt.Key_Escape:
            #print("Escape pressed. Clearing input buffer.")
            self.inputBuffer = ""
            self.bufferChanged.emit(CanvasKeyEvent(key=key,buffer=self.inputBuffer,qevent=event,model=self.model,isFinished=False))
        elif key == Qt.Key_Backspace:
            # print("Escape pressed. deleting last from input buffer.")
            self.inputBuffer = self.inputBuffer[:-1]
            self.bufferChanged.emit(CanvasKeyEvent(key=key,buffer=self.inputBuffer,qevent=event,model=self.model,isFinished=False))
        else:
            # Append character to buffer if it's a visible character.
            char = event.text()
            if char:
                self.inputBuffer += char
            self.bufferChanged.emit(CanvasKeyEvent(key=key,buffer=self.inputBuffer,qevent=event,model=self.model,isFinished=False))
        super().keyPressEvent(event)

    def _onZoomFinished(self):
        # Emit zoomFinished event.
        # For viewport, we simply send current scale and center point.
        # center = QPointF(self.width() / 2, self.height() / 2)
        # self.zoomFinished.emit(self.scale, center)
        pass

    def viewportRect(self):
        # Returns the current viewport rect in canvas coordinates.
        topLeft = (-self.offset) / self.scale
        size = self.size() / self.scale
        return QRectF(topLeft, size)

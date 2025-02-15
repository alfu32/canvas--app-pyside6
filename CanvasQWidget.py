from typing import List

from PySide6.QtCore import Signal, QRectF, QPointF, QTimer
from PySide6.QtGui import QPainter, QMouseEvent, QWheelEvent, QColor, Qt, QTransform
from PySide6.QtWidgets import QWidget

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
    feedbackDrawables:List[Drawable] = []

    def __init__(self, parent=None):
        super().__init__(parent)
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
        print("paintEvent triggered")  # Debug statement

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fill background with white.
        painter.fillRect(self.rect(), QColor("white"))

        # Apply transform.
        painter.translate(self.offset)
        painter.scale(self.scale, self.scale)

        # Draw each drawable from the model.
        painter.fillRect(self.get_transform().mapRect(self.rect()), QColor("white"))
        for drawable in self.model.drawables:
            drawable.draw(painter, self.model, self)
        for drawable in self.feedbackDrawables:
            drawable.draw(painter, self.model, self)
        painter.end()

    def get_canvas_pointer_event(self,event: QMouseEvent)->CanvasPointerEvent:
        screenPoint=event.position()
        modelPoint = self.screen_to_model(screenPoint)
        under = [d for d in self.model.drawables if d.contains(modelPoint)]
        return CanvasPointerEvent(
            screenPoint=screenPoint,
            modelPoint=modelPoint,
            targetPath=under,
            target=under[0] if len(under)>0 else None
        )


    def mousePressEvent(self, event: QMouseEvent):
        self.pointerDown.emit(self.get_canvas_pointer_event(event))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.pointerUp.emit(self.get_canvas_pointer_event(event))
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        self.pointerMove.emit(self.get_canvas_pointer_event(event))
        super().mouseMoveEvent(event)

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
        under = [d for d in self.model.drawables if d.contains(modelPoint)]
        self.zoomFinished.emit(CanvasZoomEvent(
            modelPoint=modelPoint,
            screenPoint=screenPoint,
            targetPath=under,
            target=under[0] if len(under)>0 else None,
            zoomValue=delta,
            transformMatrix=self.get_transform()

        ))
        self._zoomTimer.start()  # restart timer to detect zoom finish

    def keyReleaseEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            print(f"Enter pressed. raising buffer '{self.inputBuffer}'.")
            self.bufferFinished.emit(CanvasKeyEvent(key=key,buffer=self.inputBuffer))
            self.inputBuffer = ""
        elif key == Qt.Key_Escape:
            print("Escape pressed. Clearing input buffer.")
            self.inputBuffer = ""
            self.bufferChanged.emit(CanvasKeyEvent(key=key,buffer=self.inputBuffer))
        elif key == Qt.Key_Backspace:
            print("Escape pressed. deleting last from input buffer.")
            self.inputBuffer = self.inputBuffer[:-1]
            self.bufferChanged.emit(CanvasKeyEvent(key=key,buffer=self.inputBuffer))
        else:
            # Append character to buffer if it's a visible character.
            char = event.text()
            if char:
                self.inputBuffer += char
            self.bufferChanged.emit(CanvasKeyEvent(key=key,buffer=self.inputBuffer))
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

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel
)
from PySide6.QtCore import QRectF, Qt

import Tool
from CanvasQWidget import CanvasQWidget
from Drawable import BoxDrawable, LinkDrawable, Drawable
from events import CanvasPointerEvent, CanvasKeyEvent, CanvasZoomEvent

from tools_registry import tools_registry


# Base Drawable interface

# A box drawable with metadata (name, text, etc)

# A link drawable between two boxes

# Canvas widget

# Main Application Window
class MainWindow(QMainWindow):
    currentTool: Tool.MultipointTool =None
    def __init__(self):
        super().__init__()
        self.infoLabel = None
        self.setWindowTitle("PySide Canvas Application")
        self.canvas = CanvasQWidget()
        self.initUI()

        # For link creation: store the first selected box.
        self.pendingBox = None

        # Connect canvas signals for demonstration.
        self.canvas.pointerDown.connect(self.onPointerDown)
        self.canvas.pointerUp.connect(self.onPointerUp)
        self.canvas.pointerMove.connect(self.onPointerMove)
        self.canvas.bufferChanged.connect(self.onBufferChanged)
        self.canvas.bufferFinished.connect(self.onBufferFinished)
        self.canvas.zoomFinished.connect(self.onZoomFinished)

    def on_tool_activated(self,tool:Tool):
        print(f"Activated Tool: {tool.name}")
        self.currentTool = tool

    def on_tool_changed(self,tool:Tool,drawable:Drawable):
        print(f"Changed Tool: {tool.name} Drawable {drawable}")
        # self.currentTool = tool
        self.canvas.feedbackDrawables = [drawable]
        self.canvas.update()

    def on_tool_finished(self,tool:Tool,drawable:Drawable):
        print(f"Finished Tool: {tool.name} Drawable {drawable}")
        self.canvas.model.add_drawable(drawable)
        self.canvas.feedbackDrawables = []
        self.canvas.update()


    def initUI(self):
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)
        # Canvas takes most of the space.
        mainLayout.addWidget(self.canvas)


        self.infoLabel = QLabel("Input Buffer: (empty)")
        mainLayout.addWidget(self.infoLabel)
        # Button bar.
        buttonBar = QHBoxLayout()

        for tool in tools_registry:
            btn=tool.create_activation_button()
            # Use a lambda with a default argument to capture the current tool.
            tool.activated.connect(lambda tt: self.on_tool_activated(tt))
            tool.changed.connect(lambda tt,dd: self.on_tool_changed(tt,dd))
            tool.finished.connect(lambda tt,dd: self.on_tool_finished(tt,dd))
            buttonBar.addWidget(btn)
            tool.model=self.canvas.model
        mainLayout.addLayout(buttonBar)

    def onPointerMove(self, event:CanvasPointerEvent):
        # print("Pointer Moved through ", screenPoint, "with drawables:", [type(d).__name__ for d in drawables])
        if self.currentTool is not None:
            self.currentTool.set_last_input(event)

    def onPointerDown(self, event:CanvasPointerEvent):
        print("Pointer Down at", event.modelPoint, "with drawables:", [type(d).__name__ for d in event.targetPath])
        if self.currentTool is not None:
            pass

    def onPointerUp(self, event:CanvasPointerEvent):
        print("Pointer Up at", event.modelPoint, "with drawables:", [type(d).__name__ for d in event.targetPath])
        print(self.currentTool)
        if self.currentTool is not None:
            self.currentTool.add_input(event)
            (messages,result) =self.currentTool.drawable_class.build(self.currentTool.inputs,self.canvas.model)
            print(messages)
            print(result)
            print(self.currentTool.inputs)
            print(self.canvas.model.drawables)
            print(self.canvas.feedbackDrawables)
    def onBufferChanged(self,event:CanvasKeyEvent):
        if self.currentTool:
            print(f"Setting buffer '{event.buffer}' to tool {self.currentTool.name}.")
            self.currentTool.set_last_input(event)
        else:
            print(f"No tool is active to receive input {event.buffer}.")
        self.infoLabel.setText(f"Input Buffer: {event.buffer}")
        pass
    def onBufferFinished(self,event:CanvasKeyEvent):
        if self.currentTool:
            print(f"Buffer finished '{event.buffer}' to tool {self.currentTool.name}.")
            self.currentTool.add_input(event)
        else:
            print(f"No tool is active to receive input {event.buffer}.")
        self.infoLabel.setText(f"Input Buffer: {event.buffer}")
        pass



    def onZoomFinished(self, event:CanvasZoomEvent):
        print("Zoom finished. Scale:", event.zoomValue, "Center:", event.modelPoint)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())

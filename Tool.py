# ------------------ Tool Interface ------------------
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, QSizeF, Qt, Signal, QObject
from PySide6.QtGui import QPen, QColor
from PySide6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QLabel

from Drawable import Drawable, SelectDrawable, BoxDrawable
from events import CanvasPointerEvent, CanvasKeyEvent, CanvasEvent

if TYPE_CHECKING:  # Helps with type checking, but does nothing at runtime
    from Tool import Tool  # Forward declaration to prevent circular import

class Tool(QObject):
    activated: Signal  # Type hint (doesn't interfere with PySide)
    changed: Signal
    finished: Signal

    # Define signals as class attributes
    activated = Signal(QObject)  # Must be a class attribute
    changed = Signal(QObject, object, list)
    finished = Signal(QObject, object)

    inputs:list[CanvasEvent]
    last_pointer_event:CanvasPointerEvent
    last_key_event:CanvasKeyEvent
    def __init__(self,name:str):
        super().__init__()
        self.name = name
        self.model:'ModelDrawable' = None
        print(f"Tool({self.name})::dir{dir(self)}")
        print(f"Tool({self.name}).mro {Tool.mro()}")

    def add_input(self, input_value,tool:'Tool'):
        raise NotImplementedError

    def set_last_input(self, input_value,tool:'Tool'):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def create_activation_button(self):
        raise NotImplementedError

    def create_settings_widget(self):
        raise NotImplementedError

    def on_finished(self,drawable:Drawable):
        # Clear inputs for next construction.
        self.inputs = []



class MultipointTool(Tool):

    def __init__(self, name: str, drawable_class, parent=None):
        super().__init__(name)
        self.drawable_class = drawable_class
        self.inputs = []
        print(f"MultipointTool({self.name})::dir{dir(self)}")
        print(f"MultipointTool({self.name}).mro {Tool.mro()}")

    def add_input(self, event,tool:Tool):
        """Append an input and evaluate the accumulated inputs via the drawable's build() method."""
        self.inputs.append(event)
        errors, drawable = self.drawable_class.build(self.inputs,self.model)
        if errors == []:
            # Build complete, emit finished event.
            # should emmit the inputs
            self.last_pointer_event=[inp for inp in self.inputs if inp.type=='pointer'][-1]
            self.last_key_event=[inp for inp in self.inputs if inp.type=='key'][-1]
            self.finished.emit(self, drawable)
        else:
            # Build incomplete; simply notify listeners of the updated inputs.
            self.changed.emit(self,drawable,errors)

    def set_last_input(self, event,tool:Tool):
        """Append an input and evaluate the accumulated inputs via the drawable's build() method."""
        errors, drawable = self.drawable_class.build(self.inputs + [event],self.model)
        self.changed.emit(self, drawable,errors)

    def reset(self):
        self.inputs = []

    def create_activation_button(self):
        """Factory method to create a button with the tool's name."""
        btn = QPushButton(f"{self.name}")
        # Prevent button from stealing focus.
        btn.setFocusPolicy(Qt.NoFocus)
        btn.clicked.connect(lambda: self.activated.emit(self))
        return btn

    def create_settings_widget(self):
        """Factory method to create a simple settings widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(f"{self.name} Settings:")
        layout.addWidget(label)
        return widget

    def on_finished(self,drawable:Drawable):
        self.model.add_drawable(drawable)
        self.last_pointer_event = None
        self.last_key_event = None
        self.inputs = []

class BoxDrawableTool(MultipointTool):
    def __init__(self):
        super().__init__('Box',BoxDrawable,None)

    def on_finished(self,drawable:Drawable):
        # print(f"Finished Tool: {self.name} Drawable {drawable}")
        if self.last_pointer_event is not None:
            if self.last_pointer_event.target is not None:
                print(f"adding {drawable} to box {self.last_pointer_event.target}")
                self.last_pointer_event.target.add_child(drawable)
            else:
                print(f"adding {drawable} to root")
                self.model.add_drawable(drawable)
        else:
            print(f"adding {drawable} to root")
            self.model.add_drawable(drawable)
        self.last_pointer_event = None
        self.last_key_event = None
        self.inputs = []


class MultipointModifierTool(Tool):

    def __init__(self, name: str, drawable_class, parent=None):
        super().__init__(name)
        self.name = name
        self.drawable_class = drawable_class
        self.inputs = []
        print(f"MultipointModifierTool({self.name})::dir{dir(self)}")
        print(f"MultipointModifierTool({self.name}).mro {MultipointModifierTool.mro()}")

    def add_input(self, event,tool:Tool):
        """Append an input and evaluate the accumulated inputs via the drawable's build() method."""
        self.inputs.append(event)
        errors, drawable = self.drawable_class.build(self.inputs,self.model)
        if errors == []:
            # Build complete, emit finished event.
            # should emmit the inputs
            drawable.is_finalized=True
            self.finished.emit(self, drawable)
            # Clear inputs for next construction.
            self.inputs = []
        else:
            # Build incomplete; simply notify listeners of the updated inputs.
            self.changed.emit(self,drawable,errors)

    def set_last_input(self, event,tool:Tool):
        """Append an input and evaluate the accumulated inputs via the drawable's build() method."""
        errors, drawable = self.drawable_class.build(self.inputs + [event],self.model)
        self.changed.emit(self, drawable,errors)

    def reset(self):
        self.inputs = []

    def create_activation_button(self):
        """Factory method to create a button with the tool's name."""
        btn = QPushButton(f"{self.name}")
        # Prevent button from stealing focus.
        btn.setFocusPolicy(Qt.NoFocus)
        btn.clicked.connect(lambda: self.activated.emit(self))
        return btn

    def create_settings_widget(self):
        """Factory method to create a simple settings widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(f"{self.name} Settings:")
        layout.addWidget(label)
        return widget

    def on_finished(self,drawable:Drawable):
        # print(f"Finished Tool: {self.name} Drawable {drawable} is_finalized{drawable.is_finalized}")
        if drawable.is_finalized:
            if drawable.rtl:
                self.model.selection = self.model.find_drawables_inside(drawable.get_rect())
            else:
                self.model.selection = self.model.find_drawables_crossing(drawable.get_rect())
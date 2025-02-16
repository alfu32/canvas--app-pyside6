# ------------------ Tool Interface ------------------
from PySide6.QtCore import QPointF, QRectF, QSizeF, Qt, Signal, QObject
from PySide6.QtGui import QPen, QColor
from PySide6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QLabel

from Drawable import Drawable


class Tool:
    def __init__(self, name: str, drawable_class, parent=None):
        raise NotImplementedError

    def add_input(self, input_value):
        raise NotImplementedError

    def set_last_input(self, input_value):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def create_activation_button(self):
        raise NotImplementedError

    def create_settings_widget(self):
        raise NotImplementedError

class MultipointTool(QObject):
    # Emitted whenever an input is added.
    activated = Signal(Tool)
    changed = Signal(Tool,Drawable,list)
    # Emitted when enough inputs have been accumulated to build a complete drawable.
    finished = Signal(Tool,Drawable)
    model:'ModelDrawable'

    def __init__(self, name: str, drawable_class, parent=None):
        super().__init__(parent)
        self.name = name
        self.drawable_class = drawable_class
        self.inputs = []

    def add_input(self, event):
        """Append an input and evaluate the accumulated inputs via the drawable's build() method."""
        self.inputs.append(event)
        errors, drawable = self.drawable_class.build(self.inputs,self.model)
        if errors == []:
            # Build complete, emit finished event.
            self.finished.emit(self, drawable)
            # Clear inputs for next construction.
            self.inputs = []
        else:
            # Build incomplete; simply notify listeners of the updated inputs.
            self.changed.emit(self,drawable,errors)

    def set_last_input(self, event):
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
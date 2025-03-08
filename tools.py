import json
import os
import sys

from PySide6.QtWidgets import QApplication, QFileDialog

from Drawable import SelectDrawable
from ModelDrawable import DrawableEncoder
from Tool import MultipointModifierTool, BoxDrawableTool, OneClickTool
from Drawable import LinkDrawable
from Tool import MultipointTool


def save_model(m:'ModelDrawable'):
    print(f"saving model")
    # for d in m.get_all_linear():
    #     print(d)
    j = json.dumps({
        "struct": m.drawables,
        "index": m.get_all_linear()
    }, cls=DrawableEncoder, indent=2)
    # Ensure there's a running QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    # Open a Save File dialog
    file_path, _ = QFileDialog.getSaveFileName(
        parent=None, caption="Save File", dir="", filter="JSON Files (*.json)",selectedFilter="*.json"
    )
    print(file_path)
    if file_path:
        fd = os.open(file_path, os.O_RDWR | os.O_CREAT)
        with os.fdopen(fd, 'w+') as file:
            file.write(j)

def load_model(m:'ModelDrawable'):
    print(f"loading model")
    # for d in m.get_all_linear():
    #     print(d)
    # Ensure there's a running QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    # Open an Open File dialog
    file_path, _ = QFileDialog.getOpenFileName(
        parent=None, caption="Open File", dir="", filter="JSON Files (*.json)",selectedFilter="*.json"
    )# Open the file in read mode ('r')
    fd = os.open(file_path, os.O_RDWR | os.O_CREAT)
    with os.fdopen(fd, 'w+') as file:
        json_str = file.read()  # Reads the entire file content into a string
        m.restore_from_json(json_str)

def compile_model(m:'ModelDrawable'):
    print(f"compiling model")
    # for d in m.get_all_linear():
    #     print(d)
    for k,v in m.get_tree().items():
        print(k)

select_tool=MultipointModifierTool("Select", SelectDrawable)
drawable_box_tool=BoxDrawableTool()
link_box_tool=MultipointTool("Link", LinkDrawable)
save_model_json=OneClickTool("Save",save_model)
load_model_json=OneClickTool("Load",load_model)
compile_model_json=OneClickTool("Compile",compile_model)

from __future__ import annotations

import json
import os
import sys
from os import write
from typing import List, Dict, Any

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtWidgets import QApplication, QFileDialog

from Drawable import Drawable, BoxDrawable, LinkDrawable

class DrawableEncoder:
    pass

class ModelDrawable(Drawable):

    selection:List[Drawable] = []
    feedbackDrawables:List[Drawable] = []

    def __init__(self):
        self.selection = []
        self.drawables = []
        # Optionally store metamodel data for each box.
        self.metamodel = {}
        self.feedbackDrawables=[]

    def add_drawable(self, drawable: Drawable):
        self.drawables.append(drawable)
        # If it's a box, store its metadata.
        if isinstance(drawable, BoxDrawable):
            self.metamodel[id(drawable)] = drawable.metadata
        if isinstance(drawable, LinkDrawable):
            self.metamodel[id(drawable)] = drawable.metadata
            drawable.box1.add_link(drawable)
            drawable.box2.add_link(drawable)

    def contains(self, point: QPointF) -> bool:
        for d in self.drawables:
            if d.contains(point):
                return True
        return False

    def find_drawables_inside(self, rect: QRectF) -> List[Drawable]:
        """
        Finds all drawables that are **completely contained** within the given rectangle.
        """
        all = []
        for d in self.drawables:
            if rect.contains(d.get_rect()) or len(d.get_hotspots()) == len(
                [hs for hs in d.get_hotspots() if rect.contains(hs.point)]):
                all.append(d)
            for child in d.find_drawables_inside(rect):
                all.append(child)
        return all

    def find_drawables_crossing(self, rect: QRectF) -> List[Drawable]:
        """
        Finds all drawables that **partially overlap** (intersect) with the given rectangle.
        """
        all = []
        for d in self.drawables:
            if rect.intersects(d.get_rect()) or rect.contains(d.get_rect()) or [hs for hs in d.get_hotspots() if rect.contains(hs.point)]:
                all.append(d)
            for child in d.find_drawables_inside(rect):
                all.append(child)
        return all

    def get_all_linear(self):
        all = []
        for d in self.drawables:
            all.append(d)
            for child in d.children:
                all.append(child)
        return all

    def save_to_json(self):
        pass

    def from_json(self,json_str:str):
        pass

    def ask_save_file(self) -> str:
        # Ensure there's a running QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        # Open a Save File dialog
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save File", "", "All Files (*.*)"
        )
        j = json.dumps({
            "struct":self.drawables,
            "index":self.get_all_linear()
        }, cls=DrawableEncoder, indent=2)
        print(file_path)
        if file_path:
            fd = os.open(file_path, os.O_RDWR | os.O_CREAT)
            with os.fdopen(fd, 'w+') as file:
                file.write(j)

    def ask_open_file(self) -> str:
        # Ensure there's a running QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        # Open an Open File dialog
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open File", "", "All Files (*.*)"
        )# Open the file in read mode ('r')
        fd = os.open(file_path, os.O_RDWR | os.O_CREAT)
        with os.fdopen(fd, 'w+') as file:
            json_str = file.read()  # Reads the entire file content into a string
            data: Dict[str, Any] = json.loads(json_str)
            index={}
            for item in data["index"]:
                index[item["id"]]=item
                if item["class"] == "BoxDrawable":
                    print(item["rect"])
                    index[item["id"]] = BoxDrawable(
                        QRectF(
                            QPointF(
                                item["rect"]["topLeft"]["x"],
                                item["rect"]["topLeft"]["y"]
                            ),
                            QPointF(
                                item["rect"]["bottomRight"]["x"],
                                item["rect"]["bottomRight"]["y"]
                            )
                        ),{}
                    )
                    index[item["id"]].name=item["name"]
            for item in data["index"]:
                if item["class"] == "LinkDrawable":
                    box1:BoxDrawable = index[item["src"]["id"]]
                    box2:BoxDrawable = index[item["target"]["id"]]
                    link = LinkDrawable(
                        box1,
                        box2,
                        {}
                    )
                    link.name = item["name"]
                    box1.add_link(link)
                    box2.add_link(link)
                    index[item["id"]] = link
            for item in data["index"]:
                if item["class"] == "BoxDrawable":
                    it=index[item["id"]]
                    for childref in item["children"]:
                        it.add_child(index[childref["id"]])
            print(index)
            drawables = []
            for item in data["struct"]:
                drawables.append(index[item["id"]])
            print(drawables)
            self.drawables = drawables

class DrawableEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ModelDrawable):
            # Convert the object to a dict (customize as needed)
            return {
                "class":"ModelDrawable",
                "drawables":obj.drawables
            }
        elif isinstance(obj, BoxDrawable):
            # Convert the object to a dict (customize as needed)
            return {
                "class":"BoxDrawable",
                "id":obj.id,
                "name":obj.name,
                "children":[{"id":child.id,"name":child.name} for child in obj.children],
                "links":[{"id":link.id,"name":link.name} for link in obj.links],
                "rect":obj.rect,
            }
        elif isinstance(obj, LinkDrawable):
            # Convert the object to a dict (customize as needed)
            return {
                "class":"LinkDrawable",
                "id":obj.id,
                "name":obj.name,
                "src": {"id":obj.box1.id,"name":obj.box1.name},
                "target":{"id":obj.box2.id,"name":obj.box2.name},
                "rect":obj.rect,
            }
        elif isinstance(obj, Drawable):
            # Convert the object to a dict (customize as needed)
            return {
                "class":"Drawable",
                "id":obj.id,
                "name":obj.name,
                "rect":obj.rect,
            }
        elif isinstance(obj, QRectF):
            # Convert the object to a dict (customize as needed)
            return {
                "class":"QRectF",
                "topLeft":obj.topLeft(),
                "bottomRight":obj.bottomRight(),
                "x":obj.topLeft().x(),
                "y":obj.topLeft().y(),
                "w":obj.bottomRight().x() - obj.topLeft().x(),
                "h":obj.bottomRight().y() - obj.topLeft().y(),
            }
        elif isinstance(obj, QPointF):
            # Convert the object to a dict (customize as needed)
            return {
                "class":"QPointF",
                "x":obj.x(),
                "y":obj.y(),
            }
        # Call the default method for other types
        return super().default(obj)

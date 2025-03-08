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

    def get_tree(self,parent:str = None):
        tree = {}
        for d in self.drawables:
            tree[d.id]=d
            for child in d.children:
                subtree = child.get_tree(d.id)
                for k,v in subtree.items():
                    tree[k]=v
        return tree


    def restore_from_json(self,json_str: str) -> str:
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
            return obj.toMap()
        elif isinstance(obj, LinkDrawable):
            # Convert the object to a dict (customize as needed)
            return obj.toMap()
        elif isinstance(obj, Drawable):
            # Convert the object to a dict (customize as needed)
            return obj.toMap()
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

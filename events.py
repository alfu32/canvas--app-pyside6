from typing import List

from PySide6.QtCore import QPointF
from PySide6.QtGui import QTransform

from Drawable import Drawable


class CanvasPointerEvent:
    screenPoint:QPointF
    modelPoint:QPointF
    target:Drawable
    targetPath:List[Drawable]
    def __init__(self,screenPoint:QPointF,modelPoint:QPointF,target:Drawable,targetPath:List[Drawable]):
        self.screenPoint=screenPoint
        self.modelPoint=modelPoint
        self.target=target
        self.targetPath=targetPath

class CanvasZoomEvent:
    screenPoint:QPointF
    modelPoint:QPointF
    target:Drawable
    targetPath:List[Drawable]
    zoomValue:float
    transformMatrix:QTransform
    def __init__(self,screenPoint:QPointF,modelPoint:QPointF,target:Drawable,targetPath:List[Drawable],zoomValue:float,transformMatrix:QTransform):
        self.screenPoint=screenPoint
        self.modelPoint=modelPoint
        self.target=target
        self.targetPath=targetPath
        self.zoomValue=zoomValue
        self.transformMatrix=transformMatrix

class CanvasKeyEvent:
    key:int
    buffer:str
    def __init__(self,key:int,buffer:str):
        self.key=key
        self.buffer=buffer
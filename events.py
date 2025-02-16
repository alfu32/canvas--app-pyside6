from typing import List

from PySide6.QtCore import QPointF, QEvent
from PySide6.QtGui import QTransform



class CanvasPointerEvent:
    screenPoint:QPointF
    modelPoint:QPointF
    target:'Drawable'
    targetPath:List['Drawable']
    qevent:QEvent
    model:'ModelDrawable'
    def __init__(self,screenPoint:QPointF,modelPoint:QPointF,target:'Drawable',targetPath:List['Drawable'],qevent:QEvent,model:'ModelDrawable'):
        self.screenPoint=screenPoint
        self.modelPoint=modelPoint
        self.target=target
        self.targetPath=targetPath
        self.qevent=qevent
        self.model=model

class CanvasZoomEvent:
    screenPoint:QPointF
    modelPoint:QPointF
    target:'Drawable'
    targetPath:List['Drawable']
    zoomValue:float
    transformMatrix:QTransform
    qevent:QEvent
    model:'ModelDrawable'
    def __init__(self,screenPoint:QPointF,modelPoint:QPointF,target:'Drawable',targetPath:List['Drawable'],zoomValue:float,transformMatrix:QTransform,qevent:QEvent,model:'ModelDrawable'):
        self.screenPoint=screenPoint
        self.modelPoint=modelPoint
        self.target=target
        self.targetPath=targetPath
        self.zoomValue=zoomValue
        self.transformMatrix=transformMatrix
        self.qevent=qevent
        self.model=model

class CanvasKeyEvent:
    key:int
    buffer:str
    isFinished:bool=False
    qevent:QEvent
    model:'ModelDrawable'
    def __init__(self,key:int,buffer:str,qevent:QEvent,isFinished:bool,model:'ModelDrawable'):
        self.key=key
        self.buffer=buffer
        self.qevent=qevent
        self.model=model
        self.isFinished=isFinished
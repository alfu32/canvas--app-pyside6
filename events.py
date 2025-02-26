from typing import List

from PySide6.QtCore import QPointF, QEvent
from PySide6.QtGui import QTransform



class CanvasPointerEvent:
    type = 'pointer'
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
    type = 'wheel'
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
    type = 'key'
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

class CanvasEvent:
    type:str
    key:int
    buffer:str
    isFinished:bool=False
    zoomValue:float
    transformMatrix:QTransform
    screenPoint:QPointF
    modelPoint:QPointF
    target:'Drawable'
    targetPath:List['Drawable']
    qevent:QEvent
    model:'ModelDrawable'
    def __init__(self,screenPoint:QPointF,modelPoint:QPointF,target:'Drawable',targetPath:List['Drawable'],qevent:QEvent,model:'ModelDrawable'):
        self.type='pointer'
        self.screenPoint=screenPoint
        self.modelPoint=modelPoint
        self.target=target
        self.targetPath=targetPath
        self.qevent=qevent
        self.model=model

    def __init__(self,screenPoint:QPointF,modelPoint:QPointF,target:'Drawable',targetPath:List['Drawable'],zoomValue:float,transformMatrix:QTransform,qevent:QEvent,model:'ModelDrawable'):
        self.type='wheel'
        self.screenPoint=screenPoint
        self.modelPoint=modelPoint
        self.target=target
        self.targetPath=targetPath
        self.zoomValue=zoomValue
        self.transformMatrix=transformMatrix
        self.qevent=qevent
        self.model=model

    def __init__(self,key:int,buffer:str,qevent:QEvent,isFinished:bool,model:'ModelDrawable'):
        self.type = 'key'
        self.key=key
        self.buffer=buffer
        self.qevent=qevent
        self.model=model
        self.isFinished=isFinished
#!/usr/bin/python
# -*- coding: utf-8 -*-
class WaveDraw(object):
    def __init__(self,title=""):
        self.title=title
        self.currentClk=1
        self.signalList=[]
        self.hscale=1
        self.edgeList=[]
    
    def generateBool(self,name:str,initWave:str="0",initNode:str=".",period:float=1,phase:int=0):
        from wavedraw.WaveBool import WaveBool
        waveBool= WaveBool(name=name,wavedraw=self,initWave=initWave,initNode=initNode,period=period,phase=phase)
        self.signalList.append(waveBool)
        return waveBool
    
    def generateBits(self,name:str,initWave:str="0",initNode:str=".",initData:str=None,period:float=1,phase:int=0):
        from wavedraw.WaveBits import WaveBits
        waveBits= WaveBits(name=name,wavedraw=self,initWave=initWave,initNode=initNode,initData=initData,period=period,phase=phase)
        self.signalList.append(waveBits)
        return waveBits

    def generateGroup(self,name:str,period:float=1,phase:int=0):
        from wavedraw.WaveGroup import WaveGroup
        waveGroup=WaveGroup(name=name,wavedraw=self,period=period,phase=phase)
        self.signalList.append(waveGroup)
        return waveGroup
    
    def incrClk(self,delat:int=1):
        self.currentClk=self.currentClk+delat
    
    def addSplit(self):
        for signal in self.signalList:
            signal.addSplit()
        self.incrClk()
    
    def addEdge(self,*edges):
        for edge in edges:
            self.edgeList.append(edge)
    
    def getClockNum(self)->int:
        maxClock=0
        for signal in self.signalList:
            if signal.getClockNum()>maxClock:
                maxClock=signal.getClockNum()
        return maxClock
    
    def generateJson(self)->str:
        from wavedraw.WaveGroup import WaveGroup
        self.currentClk=self.getClockNum()+2
        wave=""
        for signal in self.signalList:
            if isinstance(signal,WaveGroup):
                wave+=f"[{signal.generateJson()}],\n"
            else:
                wave+=f"{{{signal.generateJson()}}},\n"
        edges=""
        for edge in self.edgeList:
            edges+=f"\'{edge}\',"
        if len(self.edgeList)>0:
            return f"{{\"signal\":[\n{wave}],\n\"head\":{{\"text\":\"{self.title}\",\"tick\":0}},\n\"edge\":[{edges}],\n\"config\":{{\"hscale\":{self.hscale}}}}}"
        else:
             return f"{{\"signal\":[\n{wave}],\n\"head\":{{\"text\":\"{self.title}\",\"tick\":0}},\n\"config\":{{\"hscale\":{self.hscale}}}}}"   
    
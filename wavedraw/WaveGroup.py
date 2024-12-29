#!/usr/bin/python
# -*- coding: utf-8 -*-
from wavedraw.WaveDraw import WaveDraw
from wavedraw.WaveBits import WaveBits
from wavedraw.WaveBool import WaveBool
class WaveGroup(object):
    def __init__(self,name:str,wavedraw:WaveDraw,period:float=1,phase:int=0):
        self.name=name
        self.wavedraw=wavedraw
        self.period=period
        self.phase=phase
        self.signalList=[]
    
    def generateBool(self,name:str,initWave:str="0",initNode:str=".",period:float=None,phase:int=None):
        periodAdapt=period
        phaseAdapt=phase
        if periodAdapt==None:
            periodAdapt=self.period
        if phaseAdapt==None:
            phaseAdapt=self.phase
        waveBool= WaveBool(name=name,wavedraw=self.wavedraw,initWave=initWave,initNode=initNode,period=periodAdapt,phase=phaseAdapt)
        self.signalList.append(waveBool)
        return waveBool
    
    def generateBits(self,name:str,initWave:str="0",initNode:str=".",initData:str=None,period:float=None,phase:int=None):
        periodAdapt=period
        phaseAdapt=phase
        if periodAdapt==None:
            periodAdapt=self.period
        if phaseAdapt==None:
            phaseAdapt=self.phase
        waveBits= WaveBits(name=name,wavedraw=self.wavedraw,initWave=initWave,initNode=initNode,initData=initData,period=periodAdapt,phase=phaseAdapt)
        self.signalList.append(waveBits)
        return waveBits
    
    def generateGroup(self,name:str):
        waveGroup=WaveGroup(name=name,wavedraw=self.wavedraw,period=self.period,phase=self.phase)
        self.signalList.append(waveGroup)
        return waveGroup
    
    def addSplit(self):
        for signal in self.signalList:
            signal.addSplit()
    
    def getClockNum(self)->int:
        maxClock=0
        for signal in self.signalList:
            if signal.getClockNum()>maxClock:
                maxClock=signal.getClockNum()
        return maxClock
    
    def generateJson(self)->str:
        json=f"\"{self.name}\",\n"
        for signal in self.signalList:
            if isinstance(signal,WaveGroup):
                json+=f"[{signal.generateJson()}],\n"
            else:
                json+=f"{{{signal.generateJson()}}},\n"
        return json
        

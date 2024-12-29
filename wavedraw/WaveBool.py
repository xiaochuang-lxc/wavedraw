#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from wavedraw.WaveDraw import WaveDraw
class WaveBool(object):
    def __init__(self,name:str,wavedraw:WaveDraw,initWave:str="0",initNode:str=".",period:float=1,phase:int=0):
        self.name=name
        self.wavedraw=wavedraw
        self.waveList=[initWave]
        self.nodeList=[initNode]
        self.clockTriggreDict={}
        self.period=period
        self.phase=phase
    
    def addTriggerAtClock(self,clock:int,wave:str,node:str="."):
        if wave not in ["0","1","z","u","d","p","P","n","N","|"]:
            print(f"WaveBool:{self.name} wave:{wave} at clock:{clock} is not a value value[0,1,z,u,d,p,P,n,N,|]")
            sys.exit(-1)
        if clock in self.clockTriggreDict.keys():
            print(print(f"WaveBool:{self.name} at clock:{clock} has already registered wave:{self.clockTriggreDict[clock]}"))
            sys.exit(-1)
        self.clockTriggreDict[clock]=(wave,node)
    
    def addTrigger(self,wave:str,node:str=".",offset:int=0):
        self.addTriggerAtClock(clock=self.wavedraw.currentClk+offset,wave=wave,node=node)
    
    def wave(self,wave:str,node:str=None,offset:int=0,endWave:str="0",endNode:str=".",holdCycle:int=None):
        """ add wave to signal

        Args:
            wave (str): signal wave string
            node (str, optional): signal node define. Defaults to None.
            offset (int, optional): wave start offset based on current clock time. Defaults to 0.
            endWave (str, optional): end wave string,only used when holdCycle!=None. Defaults to "x".
            endNode (str, optional):  end node string,only used when holdCycle!=None. Defaults to ".".
            holdCycle (int, optional): repeat wave holdCycle times and then end with endWave/enddata/endnode when holdCycle!=None. Defaults to None.
        """
        if holdCycle==None:
            nodeAdapt=node
            if node==None:
                nodeAdapt="."*len(wave)
            else:
                if len(node)!= len(wave):
                    print(f"WaveBool:{self.name} wave:{wave} len mismatch node:{node} len at clock:{self.wavedraw.currentClk+offset} ")
                    sys.exit(-1)
            for index in range(len(wave)):
                self.addTrigger(wave=wave[index],node=nodeAdapt[index],offset=offset+index)
        else:
            if len(wave)!=1 or len(node)!=1:
                print(f"WaveBool:{self.name} wave:{wave} and node:{node} should be one symbol when holdCycle != None")
                sys.exit(-1)
            for index in range(holdCycle):
                if index==0:
                    self.wave(wave=wave,node=node,offset=offset+index,holdCycle=None)
                else:
                    self.wave(wave=wave,node=".",offset=offset+index,holdCycle=None)
            self.wave(wave=endWave,node=endNode,offset=offset+holdCycle,holdCycle=None)
    
    def addSplit(self):
        self.addTrigger(wave="|",node=".",offset=0)
    
    def getClockNum(self)->int:
        if len(self.clockTriggreDict.keys())!=0:
            return max(self.clockTriggreDict.keys())
        else:
            return 0

    def generateJson(self)->str:
        lastValidWave=self.waveList[0]
        for clk in range(1,self.wavedraw.currentClk):
            if clk in self.clockTriggreDict.keys():
                (wave,node)=self.clockTriggreDict[clk]
                if (wave== lastValidWave):
                    self.waveList.append(".")
                else:
                    self.waveList.append(wave)
                    if not wave=="|":
                        lastValidWave=wave
                if(node==None):
                    self.nodeList.append(".")
                else:
                    self.nodeList.append(node)
            else:
                self.waveList.append(".")
                self.nodeList.append(".")
        wave="".join(self.waveList)
        node="".join(self.nodeList)
        return f"\"name\":\"{self.name}\",\"wave\":\'{wave}\',\"node\":\'{node}\',\"period\":{self.period},\"phase\":{self.phase}"
#!/usr/bin/python
# -*- coding: utf-8 -*-
from wavedraw.WaveDraw import WaveDraw
import sys
class WaveBits(object):
    def __init__(self,name:str,wavedraw:WaveDraw,initWave:str="x",initData:str=None,initNode:str=".",period:float=1,phase:int=1):
        self.name=name
        self.waveList=[initWave]
        self.wavedraw=wavedraw
        self.dataList=[]
        if not (initWave== "x" or initWave=="."):
            if (initWave!="|"):
                if initData==None:
                    print(f"WaveBits:{self.name} data:{wave} should not be None while wave={wave}:{node} len at clock:{clk}")
                    sys.exit(-1)
                self.dataList.append(initData)
        self.nodeList=[]
        self.clockTriggreDict={}
        self.period=period
        self.phase=phase
    
    def addTriggerAtClock(self,clock:int,wave:str,data:str,node:str="."):
        if wave not in ["2","3","4","5","6","7","8","9","x","|","."]:
            print(f"WaveBits:{self.name} wave:{wave} at clock:{clock} is not a value value[2,3,4,5,6,7,8,9,x,.]")
            sys.exit(-1)
        if clock in self.clockTriggreDict.keys():
            print(print(f"WaveBits:{self.name} at clock:{clock} has already registered wave:{self.clockTriggreDict[clock]}"))
            sys.exit(-1)
        dataAdapt=data
        if wave=="x" or wave==".":
            dataAdapt=None
        #elif wave!="|":
        #    if data==None:
        #        print("data should not be None while wave not in [x,|]")
        #        sys.exit(-1)
        self.clockTriggreDict[clock]=(wave,node)
        self.clockTriggreDict[clock]=(wave,node,dataAdapt)
    
    def addTrigger(self,wave:str,node:str=".",data:str=None,offset:int=0):
        self.addTriggerAtClock(clock=self.wavedraw.currentClk+offset,wave=wave,data=data,node=node)
    
    def wave(self,wave:str,data:list[str],node:str=None,offset:int=0,endWave:str="x",endData:str=None,endNode:str=".",holdCycle:int=None):
        """ add wave to signal

        Args:
            wave (str): signal wave string
            data (list[str]): wave data list
            node (str, optional): signal node define. Defaults to None.
            offset (int, optional): wave start offset based on current clock time. Defaults to 0.
            endWave (str, optional): end wave string,only used when holdCycle!=None. Defaults to "x".
            endData (str, optional):  end data string,only used when holdCycle!=None. Defaults to None.
            endNode (str, optional):  end node string,only used when holdCycle!=None. Defaults to ".".
            holdCycle (int, optional): repeat wave holdCycle times and then end with endWave/enddata/endnode when holdCycle!=None. Defaults to None.
        """
        if(holdCycle==None):
            #node process
            nodeAdapt=node
            if node==None:
                nodeAdapt="."*len(wave)
            else:
                if len(wave)!=len(node):
                    print(f"WaveBits:{self.name} wave:{wave} len mismatch node:{node} len at clock:{self.wavedraw.currentClk+offset}")
                    sys.exit(-1)
            # data process
            dataAdapt=data
            if len(wave)!=len(data):
                print(f"WaveBits:{self.name} wave:{wave} len mismatch data:{data} len at clock:{self.wavedraw.currentClk+offset}")
                sys.exit(-1)
            for index in range(len(wave)):
                self.addTrigger(wave=wave[index],node=nodeAdapt[index],data=dataAdapt[index],offset=offset+index)
        else:
            if len(wave)!=1 or len(data)!=1 or len(node)!=1:
                print(f"WaveBits:{self.name} wave:{wave} and node:{node} and data:{data} should be only one symbol when holdCycle != None")
                sys.exit(-1)
            for index in range(holdCycle):
                if index==0:
                    self.wave(wave=wave,data=data,node=node,offset=offset+index,holdCycle=None)
                else:
                    self.wave(wave=wave,data=data,node=".",offset=offset+index,holdCycle=None)
            self.wave(wave=endWave,data=[endData],node=endNode,offset=offset+holdCycle,holdCycle=None)

    
    def addSplit(self):
        self.addTrigger(wave="|",data=None,node=".",offset=0)
    
    def getClockNum(self)->int:
        if len(self.clockTriggreDict.keys())!=0:
            return max(self.clockTriggreDict.keys())
        else:
            return 0
    
    def generateJson(self)->str:
        lastValidWave=self.waveList[0]
        for clk in range(1,self.wavedraw.currentClk):
            if clk in self.clockTriggreDict.keys():
                (wave,node,data)=self.clockTriggreDict[clk]
                if(wave==lastValidWave):
                    self.waveList.append(".")
                else:
                    self.waveList.append(wave)
                    if not (wave== "x" or wave=="."):
                        if (wave!="|"):
                            if data==None:
                                print(f"WaveBits:{self.name} data:{wave} should not be None while wave={wave}:{node} len at clock:{clk}")
                                sys.exit(-1)
                            self.dataList.append(data)
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
        dataStr=""
        for index in range(len(self.dataList)):
            dataStr+=f"\"{self.dataList[index]}\""
            if not index== (len(self.dataList)-1):
                dataStr+=","
        data=",".join(self.dataList)
        return f"\"name\":\"{self.name}\",\"wave\":\'{wave}\',\"data\":[{dataStr}],\"node\":\'{node}\',\"period\":{self.period},\"phase\":{self.phase}"        

        
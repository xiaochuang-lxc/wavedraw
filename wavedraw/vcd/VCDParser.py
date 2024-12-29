#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import deque
import sys
from wavedraw.WaveDraw import WaveDraw
from wavedraw.WaveGroup import WaveGroup
from wavedraw.WaveBits import WaveBits
from wavedraw.WaveBool import WaveBool
class Signal(object):
    def __init__(self,name:str,symbol:str,isBool:bool):
        self.name=name
        self.symbol=symbol
        self.isBool=isBool
        self.valueDict={}
    
    def addEvent(self,clock:int,value:str):
        self.valueDict[clock]=value
    
    def generateWave(self,wavedraw:WaveDraw,parentGroup:WaveGroup=None,startTime:int=None,endTime:int=None,period:float=1):
        if startTime!=None and endTime!=None:
            valueDict=self.valueDict
            self.valueDict={}
            nearestTime=startTime
            if not (startTime in valueDict.keys()):
                nearestTime=None
                times=sorted(valueDict.keys())
                for time in times:
                    if time<startTime:
                        nearestTime=time
            for key in valueDict.keys():
                if (key>=nearestTime) and (key<=endTime):
                    if nearestTime!=startTime:
                        if(key==nearestTime):
                            self.valueDict[key-nearestTime]=valueDict[key]
                        else:
                            self.valueDict[key-startTime]=valueDict[key]
                    else:
                        self.valueDict[key-nearestTime]=valueDict[key]
        signalWave=None
        if self.isBool:
            if parentGroup==None:
                if 0 in self.valueDict.keys():
                    signalWave=wavedraw.generateBool(name=self.name,initWave=self.valueDict[0],period=period)
                else:
                    signalWave=wavedraw.generateBool(name=self.name,period=period)
            else:
                if 0 in self.valueDict.keys():
                    signalWave=parentGroup.generateBool(name=self.name,initWave=self.valueDict[0],period=period)
                else:
                    signalWave=parentGroup.generateBool(name=self.name,period=period)
            for (clock,value) in self.valueDict.items():
                if clock !=0:
                    signalWave.addTriggerAtClock(clock=clock,wave=value)
        else:
            currentValue=None
            currentWave=2
            if parentGroup==None:
                if 0 in self.valueDict.keys():
                    initWave="x"
                    if self.valueDict[0]!="x":
                        initWave="2"
                    currentValue=currentValue
                    signalWave=wavedraw.generateBits(name=self.name,initWave=initWave,initData=self.valueDict[0],period=period)
                else:
                    signalWave=wavedraw.generateBits(name=self.name,initWave="x",period=period)
            else:
                if 0 in self.valueDict.keys():
                    initWave="x"
                    if self.valueDict[0]!="x":
                        initWave="2"
                    currentValue=currentValue
                    signalWave=parentGroup.generateBits(name=self.name,initWave=initWave,initData=self.valueDict[0],period=period)
                else:
                    signalWave=parentGroup.generateBits(name=self.name,initWave="x",period=period)
            for clock in sorted(self.valueDict.keys()):
                if clock!=0:
                    value=self.valueDict[clock]
                    if value!="x":
                        if value!=currentValue:
                            currentWave+=1
                            if currentWave==10:
                                currentWave=2
                            currentValue=value
                            signalWave.addTriggerAtClock(clock=clock,wave=str(currentWave),data=value)
                    else:
                        signalWave.addTriggerAtClock(clock=clock,wave="x",data=value)

class Module(object):
    def __init__(self,name:str):
        self.moduleName=name
        self.signalDict={}
        self.subModuleDIct={}
    
    def addModule(self,module:'Module'):
        self.subModuleDIct[module.moduleName]=module
    
    def addSignal(self,signal:Signal):
        self.signalDict[signal.name]=signal
    
    def registerEvent(self,clock:int,symbol:str,value:str)->bool:
        signalFind=False
        for signal in self.signalDict.values():
            if signal.symbol==symbol:
                signal.addEvent(clock=clock,value=value)
        for module in self.subModuleDIct.values():
            state=module.registerEvent(clock=clock,symbol=symbol,value=value)
            if state:
                signalFind=True
        return signalFind
    
    def generateWave(self,wavedraw:WaveDraw,parentGroup:WaveGroup=None,startTime:int=None,endTime:int=None,period:float=1):
        for signal in self.signalDict.values():
            signal.generateWave(wavedraw,parentGroup,startTime,endTime,period)
        for module in self.subModuleDIct.values():
            if parentGroup==None:
                module.generateWave(wavedraw,wavedraw.generateGroup(name=module.moduleName),startTime,endTime,period=period)
            else:
                module.generateWave(wavedraw,parentGroup.generateGroup(name=module.moduleName),startTime,endTime,period=period)

        

class VCDParser(object):
    def __init__(self,fileName:str,halfClockPeriod:int):
        self.fileName=fileName
        self.moduleCtxt=[]
        self.signalCtxt=[]
        self.top=None
        self.symbolList=[]
        self.symbolDict={}
        self.halfClockPeriod=halfClockPeriod
        self.__parser()

    def __parser(self):
        modeInfoFinished=False
        moduleCtxt=[]
        signalCtxt=[]
        with open(self.fileName) as hdl:
            lines=hdl.readlines()
            for line in lines:
                curLine=line.strip()
                if curLine!="":
                    if modeInfoFinished:
                        signalCtxt.append(curLine)
                    else:
                        if curLine.startswith("$enddefinitions"):
                            modeInfoFinished=True
                        else:
                            moduleCtxt.append(curLine)
        self.__parserModule(moduleCtxt=moduleCtxt)
        self.__parserSignal(signalCtxt)
    
    def __parserModule(self,moduleCtxt:list[str]):
        moduleStack=deque()
        currentModule=None
        symbolList=[]
        for line in moduleCtxt:
            if ("$scope" in line) and ("module" in line):
                moduleName=line.split()[2]
                module=Module(name=moduleName)
                if self.top==None:
                    self.top=module
                if currentModule==None:
                    currentModule=module
                else:
                    moduleStack.append(currentModule)
                    currentModule.addModule(module)
                    currentModule=module
            if ("$var" in line):
                lineSplited=line.split()
                symbolList.append(lineSplited[3])
                signal=Signal(name=lineSplited[4],symbol=lineSplited[3],isBool=lineSplited[2]=="1")
                currentModule.addSignal(signal)
                if lineSplited[3] in self.symbolDict.keys():
                    self.symbolDict[lineSplited[3]].append(signal)
                else:
                    self.symbolDict[lineSplited[3]]=[signal]
            if "$upscope" in line:
                #current module finished
                if len(moduleStack)>0: #not only one module
                    currentModule=moduleStack.pop()
                else: #only one module
                    pass
        if len(moduleStack)>0:
            print(f"parser failed,moduleStack is Still Not emtpy:len:{len(moduleStack)}")
            sys.exit(-1)
        self.symbolList=list(set(symbolList))
    
    def __registerEvent(self,clock:int,symbol:str,value:str):
        if symbol in self.symbolList:
            for signal in self.symbolDict[symbol]:
                signal.addEvent(clock=clock,value=value)
        else:
            print(f"symbol:{symbol} not find")
            sys.exit(-1)
    
    def __parserSignal(self,signalCtxt:list[str]):
        currentClock=0
        for line in signalCtxt:
            if line.startswith("#"):
                currentClock=int(int(line[1:])/self.halfClockPeriod)
            else:
                symbolName=None
                for symbol in self.symbolList:
                    if line.endswith(symbol):
                        symbolName=symbol
                if symbolName==None:
                    print(f"can't analysis line:{line}")
                value=line[:-len(symbolName)].strip()
                if value.startswith("b"):
                    if "x" in value or "z" in value:
                        self.__registerEvent(clock=currentClock,symbol=symbolName,value="x")
                        #self.top.registerEvent(clock=currentClock,symbol=symbolName,value="x")
                    else:
                        self.__registerEvent(clock=currentClock,symbol=symbolName,value=str(hex(int(value[1:],2))))
                        #self.top.registerEvent(clock=currentClock,symbol=symbolName,value=str(hex(int(value[1:],2))))
                else:
                    if "x" in line or "z" in value:
                        self.__registerEvent(clock=currentClock,symbol=symbolName,value="x")
                        #self.top.registerEvent(clock=currentClock,symbol=symbolName,value="x")
                    else:
                        self.__registerEvent(clock=currentClock,symbol=symbolName,value=value)
                        #self.top.registerEvent(clock=currentClock,symbol=symbolName,value=value)

    def generateWave(self,title:str,startTime:int=None,endTime:int=None,period:float=1)->str:
        wave=WaveDraw(title=title)
        self.top.generateWave(wavedraw=wave,parentGroup=None,startTime=int(startTime/self.halfClockPeriod),endTime=int(endTime/self.halfClockPeriod),period=period)
        return wave.generateJson()





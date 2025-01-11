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
        #print(f"{self.name} register value:{value} at clock {clock}")
    
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

class SignalSet(Signal):
    def __init__(self, name:str,symbol:str,isBool:bool):
        super().__init__(name, symbol, isBool)
        self.bitDict={}
    
    def addBoolSignal(self,bitId:int,signal:Signal):
        self.bitDict[bitId]=signal
    
    def getClockValue(self,oldValue:int,oldValueValid:bool,clock:int):
        #find if x in this signal
        invalidValue=True
        bitValueDict={}
        for bitId,signal in self.bitDict.items():
            if clock in signal.valueDict.keys():
                if signal.valueDict[clock] not in ["1","0"]:
                    invalidValue=False
                else:
                    bitValueDict[bitId]=int(signal.valueDict[clock])
        if invalidValue:
            newValue=0
            if oldValueValid:
                newValue=oldValue
            for bitId,value in bitValueDict.items():
                #clear old value
                if ((newValue>>bitId)&0x1)==1:
                    newValue=newValue-(1<<bitId)
                #add new value
                newValue=newValue+(value<<bitId)
            return newValue
                
        else:
            return None

    
    def updateValue(self):
        clockTicks=[]
        for signal in self.bitDict.values():
            clockTicks.extend(list(signal.valueDict.keys()))
        clockSet=sorted(list(set(clockTicks)))
        #calculate clock 0 value
        oldValue=self.getClockValue(oldValue=None,oldValueValid=False,clock=0)
        if oldValue==None:
            self.addEvent(clock=0,value="x")
        else:
            self.addEvent(clock=0,value=hex(oldValue))
        #add another value
        for clock in clockSet:
            if clock!=0:
                newValue=0
                if oldValue==None:
                    newValue=self.getClockValue(oldValue=oldValue,oldValueValid=False,clock=clock)
                else:
                    newValue=self.getClockValue(oldValue=oldValue,oldValueValid=True,clock=clock)
                if newValue==None:
                    self.addEvent(clock=clock,value="x")
                    oldValue=None
                else:
                    self.addEvent(clock=clock,value=hex(newValue))
                    oldValue=newValue

class Module(object):
    def __init__(self,name:str):
        self.moduleName=name
        self.signalDict={}
        self.subModuleDIct={}
    
    def addModule(self,module:'Module'):
        self.subModuleDIct[module.moduleName]=module
    
    def addSignal(self,signal:Signal):
        self.signalDict[signal.name]=signal
    
    def hasSignal(self,signalName:str):
        if signalName in self.signalDict.keys():
            return True
        else:
            return False
    
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
            if isinstance(signal,SignalSet):
                signal.updateValue()
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
                signal=None
                if lineSplited[2]=="1" and len(lineSplited)==7: # one bit signal
                    signal=Signal(name=f"{lineSplited[4]}{lineSplited[5]}",symbol=lineSplited[3],isBool=lineSplited[2]=="1")
                    if currentModule.hasSignal(signalName=lineSplited[4]):
                        currentModule.signalDict[lineSplited[4]].addBoolSignal(bitId=int(lineSplited[5][1:-1]),signal=signal)
                    else:
                        signalSet=SignalSet(name=lineSplited[4],symbol=lineSplited[3],isBool=False)
                        currentModule.addSignal(signalSet)
                        signalSet.addBoolSignal(bitId=int(lineSplited[5][1:-1]),signal=signal)
                else:
                    if lineSplited[2]!="1" and len(lineSplited)==7:
                        if not lineSplited[5].endswith(":0]"):
                            print(f"can't analyse line:{line}")
                            sys.exit(-1)
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
            if line.startswith("$"):
                pass
            elif line.startswith("#"):
                currentClock=int(int(line[1:])/self.halfClockPeriod)
            elif line[0] in ['0','1','x','X','z','Z']: # single bit
                symbolName=line[1:]
                value=line[0]
                if value not in ['0','1']:
                    self.__registerEvent(clock=currentClock,symbol=symbolName,value="z")
                else:
                    self.__registerEvent(clock=currentClock,symbol=symbolName,value=value)
            elif line[0] in ['b','B','r','R']: # multi bit
                [value,symbolName]=line.split(" ")
                if "x" in value:
                    self.__registerEvent(clock=currentClock,symbol=symbolName,value="x")
                else:
                    self.__registerEvent(clock=currentClock,symbol=symbolName,value=str(hex(int(value[1:],2))))
            else:
                print(f"can't analyse line:{line}")
                sys.exit(-1)

    def generateWave(self,title:str,startTime:int=None,endTime:int=None,period:float=1)->str:
        wave=WaveDraw(title=title)
        if startTime==None or endTime==None:
            self.top.generateWave(wavedraw=wave,parentGroup=None,startTime=None,endTime=None,period=period)
        else:
            self.top.generateWave(wavedraw=wave,parentGroup=None,startTime=int(startTime/self.halfClockPeriod),endTime=int(endTime/self.halfClockPeriod),period=period)
        return wave.generateJson()





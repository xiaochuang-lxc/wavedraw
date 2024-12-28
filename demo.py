#!/usr/bin/python
# -*- coding: utf-8 -*-
#import sys
#sys.path.append("./")
from wavedraw.WaveDraw import *
from wavedraw.WaveGroup import *
from wavedraw.WaveBool import *
from wavedraw.WaveBits import *

wave=WaveDraw(title="demo")
clk=wave.generateBool(name="clk",initWave="P")
master=wave.generateGroup(name="Master")
ctrl=master.generateGroup(name="ctrl")
write=ctrl.generateBool(name="write",initWave="0")
read=ctrl.generateBool(name="read",initWave="0")
addr=master.generateBits(name="addr",initWave="x")
wdata=master.generateBits(name="wdata",initWave="x")

slave=wave.generateGroup(name="Slave")
ctrl=slave.generateGroup(name="ctrl")
ack=ctrl.generateBool(name="ack",initWave="0")
rdata=slave.generateBits(name="rdata",initWave="x")

# write operation
write.wave(wave="110",node="a..")
addr.wave(wave="33x",data=["A1","A1",None])
wdata.wave(wave="33x",data=["D1","D1",None])
ack.wave(wave="010",node="..b")
wave.addEdge("a->b write")

wave.incrClk(3)
wave.addSplit()
# read operation
read.wave("1110",node="c...")
addr.wave(wave="4",data=["A2"],node=".",endWave="x",holdCycle=3)
ack.wave(wave="0010",node="...d")
rdata.wave("5x",data=["Q2",None],offset=2)
wave.addEdge("c->d read")

print(wave.generateJson())
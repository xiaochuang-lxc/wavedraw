#!/usr/bin/python
# -*- coding: utf-8 -*-
#import sys
#sys.path.append("./")
from wavedraw.WaveDraw import *
from wavedraw.WaveGroup import *
from wavedraw.WaveBool import *
from wavedraw.WaveBits import *

wave=WaveDraw(title="demo1")

A=wave.generateBool(name="A")
B=wave.generateBool(name="B")
C=wave.generateBool(name="C")
D=wave.generateBool(name="D")
E=wave.generateBool(name="E")

wave.incrClk(1)
A.wave(wave="1",node="a",endNode="j",holdCycle=9)
B.wave(wave="1",node="b",endNode="i",offset=1,holdCycle=8)
C.wave(wave="1",node="c",endNode="h",offset=2,holdCycle=5)
D.wave(wave="1",node="d",endNode="g",offset=3,holdCycle=3)
E.wave(wave="1",node="d",endNode="g",offset=4,holdCycle=1)

wave.incrClk(11)
B.wave(wave="1111")
C.wave(wave="1111")
D.wave(wave="111",offset=1)
E.wave(wave="1",offset=2)

wave.addEdge('a~b t1', 'c-~a t2', 'c-~>d time 3', 'd~-e',
    'e~>f', 'f->g', 'g-~>h', 'h~>i some text', 'h~->j')

print(wave.generateJson())
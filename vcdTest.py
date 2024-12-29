#!/usr/bin/python
# -*- coding: utf-8 -*-
#import sys
#sys.path.append("./")
from wavedraw.vcd.VCDParser import *

vcdParser=VCDParser(fileName="./wave.vcd",halfClockPeriod=5)
print(vcdParser.generateWave("wave",1000,1400,period=0.5))
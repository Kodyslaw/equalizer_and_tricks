#!/usr/bin/env python3
import numpy as np
import math

class Tremolo:
    def __init__(self, czestotliwosc_hz=5.0, glebokosc=0.6, miks=1.0, ksztalt="sine"):
        self.czestotliwosc_hz = czestotliwosc_hz
        self.glebokosc = glebokosc
        self.miks = miks
        self.ksztalt = ksztalt

    def process(self, sygnal, fs):
        ramki, kanaly = sygnal.shape
        t = np.arange(ramki)/fs
        if self.ksztalt=="triangle":
            lfo = 2*np.abs(2*(t*self.czestotliwosc_hz - np.floor(t*self.czestotliwosc_hz+0.5)))-1
        else:
            lfo = np.sin(2*math.pi*self.czestotliwosc_hz*t)
        modulacja = 1 + self.glebokosc*lfo
        wyjscie = sygnal * modulacja[:,None]
        return (1-self.miks)*sygnal + self.miks*wyjscie

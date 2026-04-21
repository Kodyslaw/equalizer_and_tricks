#!/usr/bin/env python3
import numpy as np
import math

class Vibrato:
    def __init__(self, czestotliwosc_hz=5.0, glebokosc_cent=20.0, miks=1.0):
        self.czestotliwosc_hz = czestotliwosc_hz
        self.glebokosc_cent = glebokosc_cent
        self.miks = miks

    def process(self, sygnal, fs):
        ramki, kanaly = sygnal.shape
        opoznienie = int(5/1000*fs)
        bufor = np.zeros(opoznienie*2 + ramki + 5)
        lfo = np.sin(2*math.pi*self.czestotliwosc_hz*np.arange(ramki)/fs)
        wyjscie = np.zeros_like(sygnal)
        for k in range(kanaly):
            bufor[opoznienie:opoznienie+ramki] = sygnal[:,k]
            for i in range(ramki):
                pos = opoznienie + i - lfo[i]*opoznienie
                if pos < 0:
                    sample = 0.0
                else:
                    if pos >= bufor.size - 1:
                        pos = bufor.size - 2
                    lo = int(pos)
                    frac = pos - lo
                    sample = (1-frac)*bufor[lo] + frac*bufor[lo+1]
                wyjscie[i,k] = sample
        return (1-self.miks)*sygnal + self.miks*wyjscie

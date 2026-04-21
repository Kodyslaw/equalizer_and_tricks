#!/usr/bin/env python3
import numpy as np
import math

class Chorus:
    def __init__(self, czestotliwosc_hz=0.8, glebokosc_ms=10.0, miks=0.5, glosy=3, ksztalt="sine"):
        self.czestotliwosc_hz = czestotliwosc_hz
        self.glebokosc_ms = glebokosc_ms
        self.miks = miks
        self.glosy = glosy
        self.ksztalt = ksztalt

    def process(self, sygnal, fs):
        ramki, kanaly = sygnal.shape
        wyjscie = np.zeros_like(sygnal)
        opoznienie = int(self.glebokosc_ms/1000*fs)

        for k in range(kanaly):
            suma = np.zeros(ramki)
            for g in range(self.glosy):
                faza = 2*math.pi*g/self.glosy
                lfo = np.sin(2*math.pi*self.czestotliwosc_hz*np.arange(ramki)/fs + faza)
                bufor = np.zeros(opoznienie+ramki+5)
                bufor[opoznienie:opoznienie+ramki] = sygnal[:,k]
                for i in range(ramki):
                    idx = int(opoznienie + i - (lfo[i]+1)/2*opoznienie)
                    suma[i] += bufor[idx] if idx>=0 else 0
            mokry = suma/self.glosy
            wyjscie[:,k] = (1-self.miks)*sygnal[:,k] + self.miks*mokry
        return wyjscie

#!/usr/bin/env python3
import numpy as np
import math

class Flanger:
    def __init__(self, czestotliwosc_hz=0.5, glebokosc_ms=2.0, miks=0.5, sprzezenie=0.0, ksztalt="sine"):
        self.czestotliwosc_hz = czestotliwosc_hz
        self.glebokosc_ms = glebokosc_ms
        self.miks = miks
        self.sprzezenie = sprzezenie
        self.ksztalt = ksztalt

    def _lfo(self, n, fs):
        t = np.arange(n) / fs
        if self.ksztalt == "triangle":
            return 2*np.abs(2*(t*self.czestotliwosc_hz - np.floor(t*self.czestotliwosc_hz+0.5)))-1
        return np.sin(2*math.pi*self.czestotliwosc_hz*t)

    def process(self, sygnal, fs):
        ramki, kanaly = sygnal.shape
        wyjscie = np.zeros_like(sygnal)
        opoznienie = int(self.glebokosc_ms/1000*fs)

        lfo = self._lfo(ramki, fs)

        for k in range(kanaly):
            bufor = np.zeros(opoznienie+ramki+5)
            bufor[opoznienie:opoznienie+ramki] = sygnal[:,k]
            for i in range(ramki):
                idx = int(opoznienie + i - (lfo[i]+1)/2*opoznienie)
                probka = bufor[idx] if idx >= 0 else 0
                wyjscie[i,k] = (1-self.miks)*sygnal[i,k] + self.miks*probka
                bufor[opoznienie+i] += probka*self.sprzezenie
        return wyjscie

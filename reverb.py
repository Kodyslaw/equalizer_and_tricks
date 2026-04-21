#!/usr/bin/env python3
import numpy as np

class Reverb:
    def __init__(self, czas_zaniku_ms=800.0, miks=0.4):
        self.czas_zaniku_ms = czas_zaniku_ms
        self.miks = miks

    def process(self, sygnal, fs):
        opoznienie = int(self.czas_zaniku_ms/1000*fs)
        bufor = np.zeros(opoznienie)
        wyjscie = np.zeros_like(sygnal)
        for k in range(sygnal.shape[1]):
            for i in range(sygnal.shape[0]):
                idx = i % len(bufor) if len(bufor) > 0 else 0
                wyjscie[i,k] = bufor[idx] if len(bufor) > 0 else 0
                if len(bufor) > 0:
                    bufor[idx] = sygnal[i,k] + bufor[idx] * 0.5
        return (1-self.miks)*sygnal + self.miks*wyjscie

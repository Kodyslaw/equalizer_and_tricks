#!/usr/bin/env python3
import numpy as np
import math

class AutoPan:
    def __init__(self, czestotliwosc_hz=0.5, glebokosc=1.0, miks=1.0):
        # Parametry efektu auto-pan
        self.czestotliwosc_hz = czestotliwosc_hz  # Częstotliwość modulacji w Hz
        self.glebokosc = glebokosc  # Głębokość efektu (0.0 - 1.0)
        self.miks = miks  # Mieszanka sygnału: 0.0 (dry) - 1.0 (wet)

    def process(self, sygnal, fs):
        # Konwersja sygnału mono na stereo (jeśli potrzebne)
        if sygnal.ndim == 1:
            sygnal = sygnal.reshape(-1, 1)
        
        ramki, kanaly = sygnal.shape
        
        # Generowanie osi czasu
        t = np.arange(ramki)/fs
        
        # Utworzenie LFO (Low Frequency Oscillator) - sinusoida modulująca
        lfo = np.sin(2*math.pi*self.czestotliwosc_hz*t)*self.glebokosc
        lfo = np.clip(lfo, -1.0, 1.0)  # Ograniczenie zakresu LFO
        
        # Obliczenie poziomów dla kanału lewego i prawego
        lewy = (1-lfo)/2
        prawy = (1+lfo)/2
        
        # Zastosowanie panowania do każdego kanału
        wyjscie = np.zeros_like(sygnal)
        wyjscie[:,0] = sygnal[:,0]*lewy  # Kanał lewy
        if kanaly>1:
            wyjscie[:,1] = sygnal[:,1]*prawy  # Kanał prawy
        
        # Zwrot zmieszanego sygnału
        return (1-self.miks)*sygnal + self.miks*wyjscie

#!/usr/bin/env python3
import numpy as np

class Distortion:
    def __init__(self, przester=4.0, miks=0.5):
        self.przester = przester
        self.miks = miks

    def process(self, sygnal, czest_probkowania):
        wyjscie = np.zeros_like(sygnal)
        for k in range(sygnal.shape[1]):
            suchy = sygnal[:, k]
            mokry = np.tanh(suchy * self.przester)
            wyjscie[:, k] = (1-self.miks)*suchy + self.miks*mokry
        return wyjscie

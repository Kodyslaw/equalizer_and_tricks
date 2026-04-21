import numpy as np

class BandEQ:
    def __init__(self, czestotliwosc_probek):
        self.czestotliwosc_probek = czestotliwosc_probek
        
        # 17 punktów dla 16 pasm
        self.bands = np.logspace(
            np.log10(20),
            np.log10(czestotliwosc_probek / 2),
            17
        )
        
        # wzmocnienie w dB
        self.wzmocnienie_db = np.zeros(16)

    def ustaw_gain(self, band, value_db):
        """Ustaw gain w dB dla pasma od 0 do 15"""
        self.wzmocnienie_db[band] = value_db

    def process(self, sygnal):
        """
        sygnal: numpy array 1D (mono)
        zwraca: sygnal po EQ
        """
        fft_sygnal = np.fft.rfft(sygnal)
        frekwencje = np.fft.rfftfreq(len(sygnal), 1/self.czestotliwosc_probek)

        # konwersja dB -> skala liniowa
        gains_lin = 10**(self.wzmocnienie_db / 20)

        for i in range(16):
            maska = (frekwencje >= self.bands[i]) & (frekwencje < self.bands[i+1])
            fft_sygnal[maska] *= gains_lin[i]

        return np.fft.irfft(fft_sygnal)

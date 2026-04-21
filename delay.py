#!/usr/bin/env python3
import numpy as np

class Delay:
    def __init__(self, opoznienie_ms=400.0, sprzezenie=0.3, miks=0.5):
        # Opóźnienie w milisekundach
        self.opoznienie_ms = opoznienie_ms
        # Współczynnik sprzężenia zwrotnego (0-1)
        self.sprzezenie = sprzezenie
        # Współczynnik mieszania sygnału oryginalnego i opóźnionego (0-1)
        self.miks = miks

    def process(self, sygnal, czest_probkowania):
        # Liczba ramek (próbek) i kanałów audio
        ramki, kanaly = sygnal.shape
        # Konwersja opóźnienia z milisekund na liczbę próbek
        opoznienie = int(self.opoznienie_ms/1000*czest_probkowania)
        # Inicjalizacja macierzy wyjścia
        wyjscie = np.zeros_like(sygnal)

        # Przetwarzanie każdego kanału osobno
        for k in range(kanaly):
            # Bufor do przechowywania sygnału z historią
            bufor = np.zeros(opoznienie+ramki+1)
            # Załadowanie sygnału wejściowego do bufora na odpowiedniej pozycji
            bufor[opoznienie:opoznienie+ramki] = sygnal[:,k]
            # Przetwarzanie każdej próbki
            for i in range(ramki):
                # Pobranie sygnału opóźnionego
                opozniona = bufor[i] if i>=opoznienie else 0
                # Mieszanie sygnału oryginalnego z opóźnionym
                wyjscie[i,k]=(1-self.miks)*sygnal[i,k]+self.miks*opozniona
                # Dodanie sprzężenia zwrotnego do bufora
                bufor[opoznienie+i]+=opozniona*self.sprzezenie
        return wyjscie

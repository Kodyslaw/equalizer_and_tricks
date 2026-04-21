import numpy as np

class Compressor:
    def __init__(self, prog_db=-24.0, wspolczynnik=4.0,
                 czas_ataku_ms=10.0, czas_powrotu_ms=100.0,
                 wzmocnienie_db=0.0, miks=1.0):

        self.prog_db = prog_db
        self.wspolczynnik = wspolczynnik
        self.czas_ataku_ms = czas_ataku_ms
        self.czas_powrotu_ms = czas_powrotu_ms
        self.wzmocnienie_db = wzmocnienie_db
        self.miks = miks

    def process(self, sygnal, czest_probkowania):
        sygnal = np.asarray(sygnal, dtype=np.float32)
        wyjscie = np.zeros_like(sygnal)

        # współczynniki ataku / release
        atk = np.exp(-1.0 / (self.czas_ataku_ms * czest_probkowania / 1000.0))
        rel = np.exp(-1.0 / (self.czas_powrotu_ms * czest_probkowania / 1000.0))

        envelope = 0.0

        for i in range(len(sygnal)):
            x = np.max(np.abs(sygnal[i]))

            # detektor obwiedni (peak)
            if x > envelope:
                envelope = atk * envelope + (1 - atk) * x
            else:
                envelope = rel * envelope + (1 - rel) * x

            # zabezpieczenie przed log(0)
            envelope = max(envelope, 1e-8)

            #  envelope  dB
            env_db = 20.0 * np.log10(envelope)

            # redukcja gainu
            if env_db > self.prog_db:
                gain_reduction_db = (
                    self.prog_db
                    + (env_db - self.prog_db) / self.wspolczynnik
                    - env_db
                )
            else:
                gain_reduction_db = 0.0

            # makeup gain
            total_gain_db = gain_reduction_db + self.wzmocnienie_db
            gain = 10.0 ** (total_gain_db / 20.0)

            # wet / dry
            wyjscie[i] = sygnal[i] * ((1 - self.miks) + self.miks * gain)

        return wyjscie

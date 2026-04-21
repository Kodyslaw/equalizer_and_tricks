#!/usr/bin/env python3
import threading
import json
import os
import numpy as np
import soundfile as sf
import tkinter as tk
import sys
import os

def resource_path(relpath: str) -> str:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(__file__)
    return os.path.join(base, relpath)

from tkinter import ttk, filedialog, messagebox
from flanger import Flanger
from chorus import Chorus
from delay import Delay
from reverb import Reverb
from distortion import Distortion
from tremolo import Tremolo
from autopan import AutoPan
from vibrato import Vibrato
from compressor import Compressor
from bandeq import BandEQ
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Słownik opisów efektów wyświetlanych użytkownikowi
OPISY_EFEKTOW = {
    "16 Band EQ": "Zmień głośność konkretnych częstotliwości w zakresie -12dB do +12dB",
    "Flanger": "Flanger – efekt modulacyjny oparty na krótkim, cyklicznie zmiennym opóźnieniu sygnału, powodujący charakterystyczne przemiatanie widma.",
    "Chorus": "Chorus – efekt pogrubiający brzmienie poprzez sumowanie sygnału z kilkoma jego opóźnionymi i modulowanymi kopiami.",
    "Delay": "Delay – efekt echa polegający na odtwarzaniu opóźnionej kopii sygnału, z możliwością wielokrotnych powtórzeń.",
    "Reverb": "Reverb – symulacja odbić dźwięku w pomieszczeniu, nadająca sygnałowi przestrzeń i głębię.",
    "Distortion": "Distortion – efekt nieliniowy polegający na przesterowaniu sygnału i zwiększeniu liczby harmonicznych.",
    "Tremolo": "Tremolo – okresowa modulacja amplitudy sygnału powodująca rytmiczne zmiany głośności.",
    "AutoPan": "AutoPan – automatyczna modulacja panoramy stereo, przesuwająca sygnał pomiędzy kanałami.",
    "Vibrato": "Vibrato – okresowa modulacja wysokości dźwięku powodująca drganie tonu.",
    "Compressor": "Kompresor – procesor dynamiki zmniejszający różnice pomiędzy cichymi i głośnymi fragmentami sygnału."
}

class AudioFXGUI:
    def __init__(self, root):
        self.root = root
        root.title("Efekty audio — rozszerzona lista efektów")
        root.resizable(False, False)
        pad = 8

        main = ttk.Frame(root, padding=pad)
        main.grid(row=0, column=0, sticky="nsew")

        # Pole wejściowe dla ścieżki pliku WAV
        self.input_path = tk.StringVar(value="")
        ttk.Label(main, text="Plik wejściowy (WAV):").grid(row=0, column=0, sticky="w")
        entry_in = ttk.Entry(main, textvariable=self.input_path, width=55)
        entry_in.grid(row=1, column=0, columnspan=3, sticky="w")
        ttk.Button(main, text="Wybierz plik…", command=self.choose_input).grid(row=1, column=2, padx=4)

        # Pole wyjściowe dla zapisanego pliku
        self.output_path = tk.StringVar(value="")
        ttk.Label(main, text="Plik wyjściowy (WAV):").grid(row=2, column=0, sticky="w", pady=(6,0))
        entry_out = ttk.Entry(main, textvariable=self.output_path, width=55)
        entry_out.grid(row=3, column=0, columnspan=3, sticky="w")
        ttk.Button(main, text="Zapisz jako…", command=self.choose_output).grid(row=3, column=2, padx=4)

        # Wybór efektu i presetu
        ttk.Label(main, text="Efekt audio:").grid(row=4, column=0, sticky="w", pady=(8,0))
        self.effect_var = tk.StringVar(value="Flanger")
        effects = ["16 Band EQ","Flanger", "Chorus", "Delay", "Reverb", "Distortion", "Tremolo",
                   "AutoPan", "Vibrato", "Compressor"]
        effect_menu = ttk.Combobox(main, textvariable=self.effect_var,
                                   values=effects, state="readonly", width=30)
        effect_menu.grid(row=4, column=1, sticky="w", pady=(8,0))
        effect_menu.bind("<<ComboboxSelected>>", lambda e: self.on_effect_change())

        self.preset_var = tk.StringVar(value="")
        self.preset_menu = ttk.Combobox(main, textvariable=self.preset_var, state="readonly", width=25)
        self.preset_menu.grid(row=4, column=2, sticky="w", pady=(8,0))
        ttk.Button(main, text="Wczytaj preset", command=self.load_preset).grid(row=4, column=3, pady=(8,0))

        # Ramka z parametrami efektów
        params = ttk.LabelFrame(main, text="Parametry efektu", padding=pad)
        params.grid(row=5, column=0, columnspan=4, pady=(8,0), sticky="ew")

        self.rate_var = tk.DoubleVar(value=0.5)
        self.rate_frame = ttk.Frame(params)
        ttk.Label(self.rate_frame, text="Częstotliwość (Hz)").pack(anchor="w")
        self.rate_scale = tk.Scale(self.rate_frame, variable=self.rate_var, from_=0.1, to=20.0, resolution=0.1,
                                   orient="horizontal", length=420)
        self.rate_scale.pack()

        self.depth_var = tk.DoubleVar(value=2.0)
        self.depth_frame = ttk.Frame(params)
        ttk.Label(self.depth_frame, text="Głębokość (ms / względna)").pack(anchor="w")
        self.depth_scale = tk.Scale(self.depth_frame, variable=self.depth_var, from_=0.0, to=40.0, resolution=0.01,
                                    orient="horizontal", length=420)
        self.depth_scale.pack()

        self.mix_var = tk.DoubleVar(value=0.5)
        self.mix_frame = ttk.Frame(params)
        ttk.Label(self.mix_frame, text="Miks (0 = sygnał suchy, 1 = sygnał efektu)").pack(anchor="w")
        self.mix_scale = tk.Scale(self.mix_frame, variable=self.mix_var, from_=0.0, to=1.0, resolution=0.01,
                                  orient="horizontal", length=420)
        self.mix_scale.pack()

        self.feedback_var = tk.DoubleVar(value=0.0)
        self.feedback_frame = ttk.Frame(params)
        ttk.Label(self.feedback_frame, text="Sprzężenie zwrotne (-0.95 … 0.95)").pack(anchor="w")
        self.feedback_scale = tk.Scale(self.feedback_frame, variable=self.feedback_var, from_=-0.95, to=0.95, resolution=0.01,
                                       orient="horizontal", length=420)
        self.feedback_scale.pack()

        self.wave_var = tk.StringVar(value="sine")
        self.wave_frame = ttk.Frame(params)
        ttk.Label(self.wave_frame, text="Kształt LFO").pack(anchor="w")
        self.wave_combo = ttk.Combobox(self.wave_frame, textvariable=self.wave_var, values=["sine", "triangle"],
                                       state="readonly", width=12)
        self.wave_combo.pack(anchor="w")

        self.voices_var = tk.IntVar(value=3)
        self.voices_frame = ttk.Frame(params)
        ttk.Label(self.voices_frame, text="Liczba głosów (Chorus)").pack(anchor="w")
        self.voices_scale = tk.Scale(self.voices_frame, variable=self.voices_var, from_=2, to=8, resolution=1,
                                     orient="horizontal", length=200)
        self.voices_scale.pack(anchor="w")

        self.delay_time_var = tk.DoubleVar(value=400.0)
        self.delay_time_frame = ttk.Frame(params)
        ttk.Label(self.delay_time_frame, text="Czas opóźnienia (ms)").pack(anchor="w")
        self.delay_time_scale = tk.Scale(self.delay_time_frame, variable=self.delay_time_var, from_=20.0, to=2000.0,
                                         resolution=1.0, orient="horizontal", length=420)
        self.delay_time_scale.pack()

        self.delay_feedback_var = tk.DoubleVar(value=0.3)
        self.delay_feedback_frame = ttk.Frame(params)
        ttk.Label(self.delay_feedback_frame, text="Sprzężenie zwrotne opóźnienia (0 … 0.95)").pack(anchor="w")
        self.delay_feedback_scale = tk.Scale(self.delay_feedback_frame, variable=self.delay_feedback_var, from_=0.0, to=0.95,
                                             resolution=0.01, orient="horizontal", length=420)
        self.delay_feedback_scale.pack()

        self.drive_var = tk.DoubleVar(value=4.0)
        self.drive_frame = ttk.Frame(params)
        ttk.Label(self.drive_frame, text="Przesterowanie (Distortion)").pack(anchor="w")
        self.drive_scale = tk.Scale(self.drive_frame, variable=self.drive_var, from_=1.0, to=30.0, resolution=0.1,
                                   orient="horizontal", length=420)
        self.drive_scale.pack()

        self.reverb_decay_var = tk.DoubleVar(value=800.0)
        self.reverb_decay_frame = ttk.Frame(params)
        ttk.Label(self.reverb_decay_frame, text="Czas zaniku pogłosu (ms)").pack(anchor="w")
        self.reverb_decay_scale = tk.Scale(self.reverb_decay_frame, variable=self.reverb_decay_var, from_=100.0, to=5000.0,
                                           resolution=10.0, orient="horizontal", length=420)
        self.reverb_decay_scale.pack()

        self.pan_depth_var = tk.DoubleVar(value=1.0)
        self.pan_depth_frame = ttk.Frame(params)
        ttk.Label(self.pan_depth_frame, text="Głębokość panoramy (0 … 1)").pack(anchor="w")
        self.pan_depth_scale = tk.Scale(self.pan_depth_frame, variable=self.pan_depth_var, from_=0.0, to=1.0, resolution=0.01,
                                       orient="horizontal", length=420)
        self.pan_depth_scale.pack()

        self.semitones_var = tk.DoubleVar(value=0.0)
        self.semitones_frame = ttk.Frame(params)
        ttk.Label(self.semitones_frame, text="Zmiana wysokości dźwięku (półtony ±)").pack(anchor="w")
        self.semitones_scale = tk.Scale(self.semitones_frame, variable=self.semitones_var, from_=-24.0, to=24.0, resolution=0.1,
                                       orient="horizontal", length=420)
        self.semitones_scale.pack()

        self.vib_depth_var = tk.DoubleVar(value=20.0)
        self.vib_depth_frame = ttk.Frame(params)
        ttk.Label(self.vib_depth_frame, text="Głębokość wibrata (centy)").pack(anchor="w")
        self.vib_depth_scale = tk.Scale(self.vib_depth_frame, variable=self.vib_depth_var, from_=0.0, to=300.0, resolution=1.0,
                                       orient="horizontal", length=420)
        self.vib_depth_scale.pack()

        # Parametry kompresora
        self.comp_thresh_var = tk.DoubleVar(value=-24.0)
        self.comp_ratio_var = tk.DoubleVar(value=4.0)
        self.comp_attack_var = tk.DoubleVar(value=10.0)
        self.comp_release_var = tk.DoubleVar(value=100.0)
        self.comp_makeup_var = tk.DoubleVar(value=0.0)
        self.comp_mix_var = tk.DoubleVar(value=1.0)

        self.comp_frame = ttk.Frame(params)
        ttk.Label(self.comp_frame, text="Kompresor: próg (dB)").pack(anchor="w")
        self.comp_thresh_scale = tk.Scale(self.comp_frame, variable=self.comp_thresh_var, from_=-60.0, to=0.0, resolution=0.5,
                                          orient="horizontal", length=420)
        self.comp_thresh_scale.pack()
        ttk.Label(self.comp_frame, text="Kompresor: ratio").pack(anchor="w")
        self.comp_ratio_scale = tk.Scale(self.comp_frame, variable=self.comp_ratio_var, from_=1.0, to=20.0, resolution=0.1,
                                          orient="horizontal", length=420)
        self.comp_ratio_scale.pack()
        ttk.Label(self.comp_frame, text="Kompresor: czas ataku (ms)").pack(anchor="w")
        self.comp_attack_scale = tk.Scale(self.comp_frame, variable=self.comp_attack_var, from_=0.1, to=200.0, resolution=0.1,
                                          orient="horizontal", length=420)
        self.comp_attack_scale.pack()
        ttk.Label(self.comp_frame, text="Kompresor: czas powrotu (ms)").pack(anchor="w")
        self.comp_release_scale = tk.Scale(self.comp_frame, variable=self.comp_release_var, from_=1.0, to=1000.0, resolution=1.0,
                                          orient="horizontal", length=420)
        self.comp_release_scale.pack()
        ttk.Label(self.comp_frame, text="Kompresor: wzmocnienie makeup (dB)").pack(anchor="w")
        self.comp_makeup_scale = tk.Scale(self.comp_frame, variable=self.comp_makeup_var, from_=-12.0, to=12.0, resolution=0.1,
                                          orient="horizontal", length=420)
        self.comp_makeup_scale.pack()
        ttk.Label(self.comp_frame, text="Kompresor: miks").pack(anchor="w")
        self.comp_mix_scale = tk.Scale(self.comp_frame, variable=self.comp_mix_var, from_=0.0, to=1.0, resolution=0.01,
                                          orient="horizontal", length=420)
        self.comp_mix_scale.pack()

        # Parametry 16-pasmowego equalizera
        self.eq1_var = tk.DoubleVar(value=0.0)
        self.eq1_frame = ttk.Frame(params)
        ttk.Label(self.eq1_frame, text="20–40 Hz").pack(anchor="w")
        self.eq1_scale = tk.Scale(
            self.eq1_frame,
            variable=self.eq1_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq1_scale.pack()

        self.eq2_var = tk.DoubleVar(value=0.0)
        self.eq2_frame = ttk.Frame(params)
        ttk.Label(self.eq2_frame, text="40–80 Hz").pack(anchor="w")
        self.eq2_scale = tk.Scale(
            self.eq2_frame,
            variable=self.eq2_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq2_scale.pack()

        self.eq3_var = tk.DoubleVar(value=0.0)
        self.eq3_frame = ttk.Frame(params)
        ttk.Label(self.eq3_frame, text="80–160 Hz").pack(anchor="w")
        self.eq3_scale = tk.Scale(
            self.eq3_frame,
            variable=self.eq3_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq3_scale.pack()

        self.eq4_var = tk.DoubleVar(value=0.0)
        self.eq4_frame = ttk.Frame(params)
        ttk.Label(self.eq4_frame, text="160–315 Hz").pack(anchor="w")
        self.eq4_scale = tk.Scale(
            self.eq4_frame,
            variable=self.eq4_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq4_scale.pack()

        self.eq5_var = tk.DoubleVar(value=0.0)
        self.eq5_frame = ttk.Frame(params)
        ttk.Label(self.eq5_frame, text="315–630 Hz").pack(anchor="w")
        self.eq5_scale = tk.Scale(
            self.eq5_frame,
            variable=self.eq5_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq5_scale.pack()

        self.eq6_var = tk.DoubleVar(value=0.0)
        self.eq6_frame = ttk.Frame(params)
        ttk.Label(self.eq6_frame, text="630–1.25 kHz").pack(anchor="w")
        self.eq6_scale = tk.Scale(
            self.eq6_frame,
            variable=self.eq6_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq6_scale.pack()

        self.eq7_var = tk.DoubleVar(value=0.0)
        self.eq7_frame = ttk.Frame(params)
        ttk.Label(self.eq7_frame, text="1.25–2.5 kHz").pack(anchor="w")
        self.eq7_scale = tk.Scale(
            self.eq7_frame,
            variable=self.eq7_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq7_scale.pack()

        self.eq8_var = tk.DoubleVar(value=0.0)
        self.eq8_frame = ttk.Frame(params)
        ttk.Label(self.eq8_frame, text="2.5–5 kHz").pack(anchor="w")
        self.eq8_scale = tk.Scale(
            self.eq8_frame,
            variable=self.eq8_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq8_scale.pack()

        self.eq9_var = tk.DoubleVar(value=0.0)
        self.eq9_frame = ttk.Frame(params)
        ttk.Label(self.eq9_frame, text="5–10 kHz").pack(anchor="w")
        self.eq9_scale = tk.Scale(
            self.eq9_frame,
            variable=self.eq9_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq9_scale.pack()

        self.eq10_var = tk.DoubleVar(value=0.0)
        self.eq10_frame = ttk.Frame(params)
        ttk.Label(self.eq10_frame, text="10–12 kHz").pack(anchor="w")
        self.eq10_scale = tk.Scale(
            self.eq10_frame,
            variable=self.eq10_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq10_scale.pack()

        self.eq11_var = tk.DoubleVar(value=0.0)
        self.eq11_frame = ttk.Frame(params)
        ttk.Label(self.eq11_frame, text="12–14 kHz").pack(anchor="w")
        self.eq11_scale = tk.Scale(
            self.eq11_frame,
            variable=self.eq11_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq11_scale.pack()

        self.eq12_var = tk.DoubleVar(value=0.0)
        self.eq12_frame = ttk.Frame(params)
        ttk.Label(self.eq12_frame, text="14–16 kHz").pack(anchor="w")
        self.eq12_scale = tk.Scale(
            self.eq12_frame,
            variable=self.eq12_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq12_scale.pack()

        self.eq13_var = tk.DoubleVar(value=0.0)
        self.eq13_frame = ttk.Frame(params)
        ttk.Label(self.eq13_frame, text="16–18 kHz").pack(anchor="w")
        self.eq13_scale = tk.Scale(
            self.eq13_frame,
            variable=self.eq13_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq13_scale.pack()

        self.eq14_var = tk.DoubleVar(value=0.0)
        self.eq14_frame = ttk.Frame(params)
        ttk.Label(self.eq14_frame, text="18–20 kHz").pack(anchor="w")
        self.eq14_scale = tk.Scale(
            self.eq14_frame,
            variable=self.eq14_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq14_scale.pack()

        self.eq15_var = tk.DoubleVar(value=0.0)
        self.eq15_frame = ttk.Frame(params)
        ttk.Label(self.eq15_frame, text="20–22 kHz").pack(anchor="w")
        self.eq15_scale = tk.Scale(
            self.eq15_frame,
            variable=self.eq15_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq15_scale.pack()

        self.eq16_var = tk.DoubleVar(value=0.0)
        self.eq16_frame = ttk.Frame(params)
        ttk.Label(self.eq16_frame, text="22–24 kHz").pack(anchor="w")
        self.eq16_scale = tk.Scale(
            self.eq16_frame,
            variable=self.eq16_var,
            from_=-12.0, to=12.0, resolution=0.1,
            orient="horizontal", length=420,command=lambda _: self.update_eq_plot()
        )
        self.eq16_scale.pack()
        
        # Lista wszystkich zmiennych EQ
        self.eq_vars = [
            self.eq1_var, self.eq2_var, self.eq3_var, self.eq4_var,
            self.eq5_var, self.eq6_var, self.eq7_var, self.eq8_var,
            self.eq9_var, self.eq10_var, self.eq11_var, self.eq12_var,
            self.eq13_var, self.eq14_var, self.eq15_var, self.eq16_var
        ]

        # Czętotliwości środkowe pasm EQ
        EQ_FREQS = [
            31, 63, 125, 250, 500, 1000, 2000, 4000,6000, 8000, 10000, 12000, 14000, 16000, 18000, 20000
        ]

        # Inicjalizacja wykresu EQ
        self.eq_plot_frame = ttk.Frame(params)
        self.eq_plot_frame.grid(row=0, column=1, rowspan=30, padx=30, sticky="n")
        self.eq_fig = Figure(figsize=(5, 4), dpi=100)
        self.eq_ax = self.eq_fig.add_subplot(111)

        self.eq_ax.set_xscale("log")
        self.eq_ax.set_xlim(20, 20000)
        self.eq_ax.set_ylim(-12, 12)

        self.eq_ax.set_xlabel("Częstotliwość (Hz)")
        self.eq_ax.set_ylabel("Wzmocnienie (dB)")
        self.eq_ax.grid(True, which="both", linestyle="--", alpha=0.4)

        self.eq_line, = self.eq_ax.plot(EQ_FREQS, [0]*16, marker="o")

        self.eq_canvas = FigureCanvasTkAgg(self.eq_fig, master=self.eq_plot_frame)
        self.eq_canvas.draw()
        self.eq_canvas.get_tk_widget().pack()

        # Umieszczenie ramek parametrów w siatce
        frames = [
            self.rate_frame, self.depth_frame, self.mix_frame, self.feedback_frame, self.wave_frame,
            self.voices_frame, self.delay_time_frame, self.delay_feedback_frame, self.drive_frame,
            self.reverb_decay_frame, self.pan_depth_frame, self.semitones_frame, self.vib_depth_frame,
            self.comp_frame, 
        ]
        for i, f in enumerate(frames):
            f.grid(row=i, column=0, sticky="w", pady=(0,6))

        # Przyciski sterowania
        buttons = ttk.Frame(main)
        buttons.grid(row=6, column=0, columnspan=4, pady=(12,0))
        self.run_btn = ttk.Button(buttons, text="Zastosuj efekt", command=self.on_run)
        self.run_btn.grid(row=0, column=0, padx=(0,6))
        ttk.Button(buttons, text="Zamknij", command=root.quit).grid(row=0, column=1)

        # Pasek statusu
        self.status_var = tk.StringVar(value="Gotowe.")
        ttk.Label(main, textvariable=self.status_var).grid(row=7, column=0, columnspan=4, sticky="w", pady=(8,0))

        self.presets = self.load_presets_from_file()
        self.update_param_visibility()
        self.update_preset_menu()

    def update_eq_plot(self, *_):
        """Aktualizuje wykres charakterystyki equalizera"""
        gains = [
        self.eq1_var.get(), self.eq2_var.get(), self.eq3_var.get(), self.eq4_var.get(),
        self.eq5_var.get(), self.eq6_var.get(), self.eq7_var.get(), self.eq8_var.get(),
        self.eq9_var.get(), self.eq10_var.get(), self.eq11_var.get(), self.eq12_var.get(),
        self.eq13_var.get(), self.eq14_var.get(), self.eq15_var.get(), self.eq16_var.get()
        ]

        self.eq_line.set_ydata(gains)
        self.eq_canvas.draw_idle()

    def on_effect_change(self):
        """Obsługa zmiany wybranego efektu"""
        self.update_param_visibility()
        efekt = self.effect_var.get()
        if efekt in OPISY_EFEKTOW:
            messagebox.showinfo(f"Opis efektu: {efekt}", OPISY_EFEKTOW[efekt])

    def load_presets_from_file(self):
        """Wczytuje presety z pliku JSON"""
        presets_path = resource_path("presets.json")
        if not os.path.isfile(presets_path):
            return {}
        try:
            with open(presets_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Preset error", f"Nie można załadować presets.json:\n{e}")
            return {}

    def update_preset_menu(self):
        """Aktualizuje listę dostępnych presetów dla wybranego efektu"""
        effect = self.effect_var.get()
        if not isinstance(self.presets, dict) or effect not in self.presets:
            self.preset_menu["values"] = []
            self.preset_var.set("")
            return
        names = list(self.presets[effect].keys())
        self.preset_menu["values"] = names
        if names:
            if self.preset_var.get() not in names:
                self.preset_var.set(names[0])

    def load_preset(self):
        """Ładuje wybrany preset i ustawia parametry"""
        effect = self.effect_var.get()
        preset_name = self.preset_var.get()
        if effect not in self.presets or preset_name not in self.presets[effect]:
            messagebox.showwarning("Brak presetu", "Brak wybranego presetu dla tego efektu.")
            return
        p = self.presets[effect][preset_name]

        if effect == "16 Band EQ" and "eq_gains" in p:
            gains = p["eq_gains"]
            if len(gains) == 16:
                for var, val in zip(self.eq_vars, gains):
                    var.set(val)
                self.update_eq_plot()

        def sset(k, var):
            if k in p:
                var.set(p[k])
        sset("rate_hz", self.rate_var)
        sset("depth_ms", self.depth_var)
        sset("depth", self.depth_var)
        sset("mix", self.mix_var)
        sset("feedback", self.feedback_var)
        sset("waveform", self.wave_var)
        sset("voices", self.voices_var)
        sset("delay_ms", self.delay_time_var)
        sset("delay_time_ms", self.delay_time_var)
        sset("delay_feedback", self.delay_feedback_var)
        sset("drive", self.drive_var)
        sset("decay_ms", self.reverb_decay_var)
        sset("pan_depth", self.pan_depth_var)
        sset("semitones", self.semitones_var)
        sset("vib_depth", self.vib_depth_var)
        sset("threshold_db", self.comp_thresh_var)
        sset("ratio", self.comp_ratio_var)
        sset("attack_ms", self.comp_attack_var)
        sset("release_ms", self.comp_release_var)
        sset("makeup_db", self.comp_makeup_var)
        sset("comp_mix", self.comp_mix_var)
        self.set_status(f"Załadowano preset: {preset_name}")

    def choose_input(self):
        """Otwiera dialog wyboru pliku wejściowego"""
        path = filedialog.askopenfilename(title="Wybierz WAV", filetypes=[("WAV files", "*.wav"), ("All files", "*.*")])
        if path:
            self.input_path.set(path)
            if not self.output_path.get():
                suggested = path.rsplit(".", 1)[0] + "_fx.wav"
                self.output_path.set(suggested)

    def choose_output(self):
        """Otwiera dialog wyboru pliku wyjściowego"""
        path = filedialog.asksaveasfilename(title="Zapisz plik jako", defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if path:
            self.output_path.set(path)

    def set_status(self, text):
        """Aktualizuje tekst statusu"""
        self.status_var.set(text)
        self.root.update_idletasks()

    def update_param_visibility(self):
        """Pokazuje/ukrywa parametry w zależności od wybranego efektu"""
        effect = self.effect_var.get()
        frames_all = [
            self.rate_frame, self.depth_frame, self.mix_frame, self.feedback_frame, self.wave_frame,
            self.voices_frame, self.delay_time_frame, self.delay_feedback_frame, self.drive_frame,
            self.reverb_decay_frame, self.pan_depth_frame, self.semitones_frame, self.vib_depth_frame,
            self.comp_frame, self.eq1_frame, self.eq2_frame, self.eq3_frame, self.eq4_frame,
            self.eq5_frame, self.eq6_frame, self.eq7_frame, self.eq8_frame,
            self.eq9_frame, self.eq10_frame, self.eq11_frame, self.eq12_frame,
            self.eq13_frame, self.eq14_frame, self.eq15_frame, self.eq16_frame, self.eq_plot_frame                         
        ]
        for f in frames_all:
            f.grid_remove()
        if effect == "Flanger":
            self.rate_frame.grid()
            self.depth_frame.grid()
            self.mix_frame.grid()
            self.feedback_frame.grid()
            self.wave_frame.grid()
            self.depth_scale.config(from_=0.2, to=10.0, resolution=0.1)
        elif effect == "16 Band EQ":
            self.eq_plot_frame.grid(
                row=0, column=1, rowspan=20, padx=10, sticky="n")
            eq_frames = [
            self.eq1_frame, self.eq2_frame, self.eq3_frame, self.eq4_frame,
            self.eq5_frame, self.eq6_frame, self.eq7_frame, self.eq8_frame,
            self.eq9_frame, self.eq10_frame, self.eq11_frame, self.eq12_frame,
            self.eq13_frame, self.eq14_frame, self.eq15_frame, self.eq16_frame
            ]
            for i, f in enumerate(eq_frames):
                f.grid(row=i, column=0, sticky="w", pady=2)
        elif effect == "Chorus":
            self.rate_frame.grid()
            self.depth_frame.grid()
            self.mix_frame.grid()
            self.wave_frame.grid()
            self.voices_frame.grid()
            self.depth_scale.config(from_=1.0, to=40.0, resolution=0.1)
        elif effect == "Delay":
            self.delay_time_frame.grid()
            self.delay_feedback_frame.grid()
            self.mix_frame.grid()
        elif effect == "Reverb":
            self.reverb_decay_frame.grid()
            self.mix_frame.grid()
        elif effect == "Distortion":
            self.drive_frame.grid()
            self.mix_frame.grid()
        elif effect == "Tremolo":
            self.rate_frame.grid()
            self.depth_frame.grid()
            self.mix_frame.grid()
            self.wave_frame.grid()
            self.depth_scale.config(from_=0.0, to=1.0, resolution=0.01)
        elif effect == "AutoPan":
            self.rate_frame.grid()
            self.pan_depth_frame.grid()
            self.mix_frame.grid()
        elif effect == "Vibrato":
            self.rate_frame.grid()
            self.vib_depth_frame.grid()
            self.mix_frame.grid()
        elif effect == "Compressor":
            self.comp_frame.grid()
        else:
            self.mix_frame.grid()
        self.update_preset_menu()

    def on_run(self):
        """Obsługa kliknięcia przycisku 'Zastosuj efekt'"""
        inp = self.input_path.get().strip()
        out = self.output_path.get().strip()
        if not inp:
            messagebox.showwarning("Brak pliku wejściowego", "Wybierz plik wejściowy .wav")
            return
        if not out:
            messagebox.showwarning("Brak pliku wyjściowego", "Wybierz plik wyjściowy (save as...)")
            return
        
        # Zbieranie parametrów z interfejsu
        params = {
            "rate_hz": float(self.rate_var.get()),
            "depth_ms": float(self.depth_var.get()),
            "depth": float(self.depth_var.get()),
            "mix": float(self.mix_var.get()),
            "feedback": float(self.feedback_var.get()),
            "waveform": self.wave_var.get(),
            "voices": int(self.voices_var.get()),
            "delay_time_ms": float(self.delay_time_var.get()),
            "delay_feedback": float(self.delay_feedback_var.get()),
            "drive": float(self.drive_var.get()),
            "decay_ms": float(self.reverb_decay_var.get()),
            "pan_depth": float(self.pan_depth_var.get()),
            "semitones": float(self.semitones_var.get()),
            "vib_depth": float(self.vib_depth_var.get()),
            "threshold_db": float(self.comp_thresh_var.get()),
            "ratio": float(self.comp_ratio_var.get()),
            "attack_ms": float(self.comp_attack_var.get()),
            "release_ms": float(self.comp_release_var.get()),
            "makeup_db": float(self.comp_makeup_var.get()),
            "comp_mix": float(self.comp_mix_var.get()),
            "eq_gains": [
                     self.eq1_var.get(), self.eq2_var.get(), self.eq3_var.get(), self.eq4_var.get(),
                     self.eq5_var.get(), self.eq6_var.get(), self.eq7_var.get(), self.eq8_var.get(),
                     self.eq9_var.get(), self.eq10_var.get(), self.eq11_var.get(), self.eq12_var.get(),
                     self.eq13_var.get(), self.eq14_var.get(), self.eq15_var.get(), self.eq16_var.get()
                    ]
        }
        self.run_btn.config(state="disabled")
        self.set_status("Przetwarzanie... ")
        # Przetwarzanie w osobnym wątku aby nie zawieszać interfejs
        thread = threading.Thread(target=self.process_and_save, args=(inp, out, params), daemon=True)
        thread.start()

    def process_and_save(self, inp, out, params):
        """Wczytuje plik WAV, stosuje efekt i zapisuje wynik"""
        try:
            data, sr = sf.read(inp, always_2d=True)
        except Exception as e:
            messagebox.showerror("Błąd czytania pliku", f"Nie można odczytać pliku:\n{e}")
            self.set_status("Błąd: nie odczytano pliku.")
            self.run_btn.config(state="normal")
            return
        if data.dtype != np.float32:
            data = data.astype(np.float32)
        effect = self.effect_var.get()
        try:
            # Aplikowanie wybranego efektu
            if effect == "Flanger":
                fl = Flanger(czestotliwosc_hz=params['rate_hz'], glebokosc_ms=params['depth_ms'],
                             miks=params['mix'], sprzezenie=params['feedback'], ksztalt=params['waveform'])
                processed = fl.process(data, sr)
            elif effect == "Chorus":
                ch = Chorus(czestotliwosc_hz=params['rate_hz'], glebokosc_ms=params['depth_ms'],
                            miks=params['mix'], glosy=params['voices'], ksztalt=params['waveform'])
                processed = ch.process(data, sr)
            elif effect == "Delay":
                d = Delay(opoznienie_ms=params['delay_time_ms'], sprzezenie=params['delay_feedback'], miks=params['mix'])
                processed = d.process(data, sr)
            elif effect == "Reverb":
                r = Reverb(czas_zaniku_ms=params['decay_ms'], miks=params['mix'])
                processed = r.process(data, sr)
            elif effect == "Distortion":
                dist = Distortion(przester=params['drive'], miks=params['mix'])
                processed = dist.process(data, sr)
            elif effect == "Tremolo":
                trem = Tremolo(czestotliwosc_hz=params['rate_hz'], glebokosc=params['depth'], miks=params['mix'],ksztalt=params['waveform'])
                processed = trem.process(data, sr)
            elif effect == "AutoPan":
                ap = AutoPan(czestotliwosc_hz=params['rate_hz'], glebokosc=params['pan_depth'], miks=params['mix']) 
                processed = ap.process(data, sr)
            elif effect == "Vibrato":
                v = Vibrato(czestotliwosc_hz=params['rate_hz'], glebokosc_cent=params['vib_depth'], miks=params['mix'])
                processed = v.process(data, sr)
            elif effect == "Compressor":
                c = Compressor(prog_db=params['threshold_db'], wspolczynnik=params['ratio'],
                               czas_ataku_ms=params['attack_ms'], czas_powrotu_ms=params['release_ms'],
                               wzmocnienie_db=params['makeup_db'], miks=params['comp_mix'])
                processed = c.process(data, sr)
            elif effect == "16 Band EQ":
                eq = BandEQ(sr)
                for i, g in enumerate(params["eq_gains"]):
                        eq.ustaw_gain(i, g)
                processed = eq.process(data[:,0] if data.ndim > 1 else data)
            else:
                processed = data
        except Exception as e:
            messagebox.showerror("Błąd przetwarzania", f"Błąd w procesie efektu:\n{e}")
            self.set_status("Błąd przetwarzania.")
            self.run_btn.config(state="normal")
            return
        try:
            sf.write(out, processed, sr, subtype='FLOAT')
        except Exception as e:
            messagebox.showerror("Błąd zapisu", f"Nie można zapisać pliku wyjściowego:\n{e}")
            self.set_status("Błąd zapisu.")
            self.run_btn.config(state="normal")
            return
        self.set_status(f"Gotowe — zapisano: {out}")
        messagebox.showinfo("Zakończono", f"Plik wyjściowy zapisano:\n{out}")
        self.run_btn.config(state="normal")

def main():
    root = tk.Tk()
    AudioFXGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

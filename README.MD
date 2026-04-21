# Efekty audio – Flanger / Chorus / Opóźnienie (Tkinter GUI)

Projekt zawiera prosty interfejs do nakładania efektów audio na pliki WAV:
- Flanger
- Chorus
- Opóźnienie

Efekty są zaimplementowane jako osobne klasy w plikach:
- `flanger.py`
- `chorus.py`
- `delay.py`

GUI znajduje się w pliku:
- `audio_fx_gui.py`

## Wymagania
Zainstaluj zależności:
pip install -r requirements.txt

## Uruchom skrypt
python audio_fx_gui.py

## Próbka
W głównym katalogu znajduje się przykładowy plik audio, którego użyto do testowania działania programu.

## Presety
Opcjonalne presety znajdują się w `presets.json`.
Możesz rozszerzyć GUI o przycisk „Załaduj preset”.

## katalog Kompilacja do EXE
W folderze EXE BUILD znajduje się gotowy plik .exe, który działa bez instalowania bibliotek i bez Pythona. 
Dołączono też skrót do głownego folderu uruchamiający aplikację.
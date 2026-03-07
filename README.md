# 🎙️ Whisper Transcription GUI

Interface graphique locale pour transcrire des fichiers audio en texte, basée sur [OpenAI Whisper](https://github.com/openai/whisper).

**100% local — aucune donnée envoyée sur internet.**

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Whisper](https://img.shields.io/badge/OpenAI-Whisper-orange) ![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green) ![License](https://img.shields.io/badge/License-MIT-lightgrey)

## ✨ Fonctionnalités

- 🖱️ **Glisser-déposer** de fichiers audio directement dans la fenêtre
- 📂 **Bouton Parcourir** pour sélectionner un fichier
- 🌍 **Multi-langues** : Français, Anglais, Espagnol, Allemand, Italien, Portugais, Néerlandais, Auto-détection
- 🧠 **Choix du modèle** : tiny / base / small / medium / large
- 📋 **Copier** le texte en un clic
- 💾 **Sauvegarder** la transcription en `.txt`
- 🎨 Interface sombre moderne (dark theme)

## 🖥️ Formats audio supportés

`MP3` `WAV` `M4A` `OGG` `FLAC` `AAC` `WMA` `OPUS`

## ⚙️ Prérequis

- Python 3.9+
- [FFmpeg](https://ffmpeg.org/) installé et dans le PATH

## 📦 Installation

```bash
# 1. Cloner le repo
git clone https://github.com/Ayhzer/whisper-transcription-gui.git
cd whisper-transcription-gui

# 2. Installer les dépendances
pip install openai-whisper tkinterdnd2

# 3. Installer FFmpeg (Windows)
winget install ffmpeg

# 4. Lancer l'application
python whisper_gui.py
```

> ⚠️ **Windows uniquement** : si `tkinterdnd2` ne se charge pas via double-clic, installez-le en **administrateur** :
> ```
> pip install tkinterdnd2 --force-reinstall
> ```

## 🚀 Utilisation

1. Glissez-déposez votre fichier audio dans la zone dédiée (ou cliquez **Parcourir**)
2. Sélectionnez le modèle et la langue
3. Cliquez **Lancer la transcription**
4. Copiez ou sauvegardez le résultat

### Choix du modèle

| Modèle | Vitesse | Précision | RAM requise |
|--------|---------|-----------|-------------|
| tiny   | ⚡⚡⚡⚡  | ⭐⭐       | ~1 Go       |
| base   | ⚡⚡⚡   | ⭐⭐⭐     | ~1 Go       |
| small  | ⚡⚡    | ⭐⭐⭐⭐   | ~2 Go       |
| medium | ⚡     | ⭐⭐⭐⭐⭐  | ~5 Go       |
| large  | 🐢     | ⭐⭐⭐⭐⭐  | ~10 Go      |

## 📝 Notes

- Le modèle est téléchargé automatiquement au premier lancement (~140 Mo pour `base`)
- Le warning `FP16 is not supported on CPU` est supprimé automatiquement (comportement normal sans GPU)
- Fonctionne entièrement hors-ligne après le premier téléchargement du modèle

## 📄 Licence

MIT — libre d'utilisation, modification et distribution.

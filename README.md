# 🎙️ Whisper Transcription GUI

Interface graphique locale pour transcrire des fichiers audio en texte, basée sur [OpenAI Whisper](https://github.com/openai/whisper).

**100% local — aucune donnée envoyée sur internet.**

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Whisper](https://img.shields.io/badge/OpenAI-Whisper-orange) ![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green) ![License](https://img.shields.io/badge/License-MIT-lightgrey)

## ✨ Fonctionnalités

- 🖱️ **Glisser-déposer** d'un ou plusieurs fichiers audio en une fois
- 📂 **Bouton Parcourir** pour sélectionner un ou plusieurs fichiers (multi-sélection)
- 📦 **Mode batch** : traitement séquentiel de tous les fichiers, sauvegarde automatique d'un `.txt` par fichier (même nom, même dossier)
- 📋 **Liste scrollable** des fichiers chargés avec compteur et bouton "Vider la liste"
- 🌍 **Multi-langues** : Français, Anglais, Espagnol, Allemand, Italien, Portugais, Néerlandais, Auto-détection
- 🧠 **Choix du modèle** : tiny / base / small / medium / large
- 📊 **Log de progression** en temps réel (fichier X/N, mots détectés, résumé final)
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

### Fichier unique
1. Glissez-déposez un fichier audio dans la zone dédiée (ou cliquez **Parcourir**)
2. Sélectionnez le modèle et la langue
3. Cliquez **Lancer la transcription**
4. Un fichier `.txt` est automatiquement créé à côté du fichier audio

### Mode batch
1. Glissez-déposez **plusieurs fichiers** d'un coup (ou Parcourir avec multi-sélection)
2. La liste des fichiers s'affiche — vous pouvez en ajouter d'autres par vagues
3. Sélectionnez le modèle et la langue, puis cliquez **Lancer la transcription**
4. Chaque fichier est traité séquentiellement, un `.txt` est créé automatiquement pour chacun
5. Le log affiche la progression en temps réel et un résumé final

### Choix du modèle

| Modèle | Vitesse | Précision | RAM requise |
|--------|---------|-----------|-------------|
| tiny   | ⚡⚡⚡⚡  | ⭐⭐       | ~1 Go       |
| base   | ⚡⚡⚡   | ⭐⭐⭐     | ~1 Go       |
| small  | ⚡⚡    | ⭐⭐⭐⭐   | ~2 Go       |
| medium | ⚡     | ⭐⭐⭐⭐⭐  | ~5 Go       |
| large  | 🐢     | ⭐⭐⭐⭐⭐  | ~10 Go      |

## 📝 Notes

- Le modèle est téléchargé automatiquement au premier lancement (~140 Mo pour `base`, ~1.5 Go pour `medium`)
- Les modèles sont mis en cache dans `~/.cache/whisper/` et réutilisés lors des lancements suivants
- Le warning `FP16 is not supported on CPU` est supprimé automatiquement (comportement normal sans GPU)
- Fonctionne entièrement hors-ligne après le premier téléchargement du modèle
- En mode batch, le modèle n'est chargé qu'une seule fois pour tous les fichiers

## 📄 Licence

MIT — libre d'utilisation, modification et distribution.

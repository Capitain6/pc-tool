# 💻 PC Tool v4.1

> Outil d'entretien et de maintenance Windows — tout-en-un, gratuit et open source.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-4.1-orange)

---

## 📸 Aperçu

PC Tool est une application de bureau Windows développée en Python avec CustomTkinter.  
Elle regroupe en un seul endroit tous les outils dont vous avez besoin pour entretenir, surveiller et réparer votre PC.

---

## ✨ Fonctionnalités

| Module | Fonctions |
|---|---|
| 📊 **Dashboard** | Score de santé, métriques temps réel, alertes système, graphiques CPU/RAM |
| 📈 **Moniteur** | Liste des processus avec CPU/RAM, tri, filtre, kill process |
| 🖥 **Système** | Infos CPU, GPU, RAM, disques, températures, pilotes, uptime |
| 🧹 **Nettoyage** | Temp, corbeille, DNS, SFC, DISM, gros fichiers, points restauration |
| 🔒 **Sécurité** | Scan antivirus Defender, détection bloatware, ports suspects, WiFi, comptes admin |
| 🌐 **Réseau** | IP locale/publique, ping, traceroute, benchmark DNS, scan réseau local |
| 🔧 **Outils Windows** | Capture d'écran, hash SHA-256, raccourcis vers tous les outils système |
| 🗑 **Désinstalleur** | Désinstallation en masse, détection automatique des logiciels suspects |
| 📄 **Rapport** | Export rapport système en `.txt` ou `.pdf` |
| 📋 **Historique** | Journal complet de toutes les actions |

### Autres fonctionnalités
- 🌙 Thème clair / sombre
- 🎨 8 couleurs d'accent personnalisables
- 🇫🇷 / 🇬🇧 Interface en français et anglais
- 🔔 Alertes système configurables (CPU, RAM, disque, uptime)
- ⏰ Nettoyage planifié automatique (jour + heure)
- 🖥 Icône dans la barre des tâches système (tray)
- ⌨️ Raccourcis clavier (`Ctrl+S`, `Ctrl+L`, `F5`, `Echap`)
- ✅ Confirmations avant toute action destructive

---

## 📦 Installation

### Option 1 — Exécutable Windows (recommandé)

Télécharge le fichier `PCTool_Setup.exe` depuis la page [**Releases**](../../releases).  
Lance l'installeur et suis les instructions.

> ⚠️ Windows Defender peut afficher un avertissement "application inconnue" car l'exe n'est pas signé.  
> Clique sur **"Informations complémentaires" → "Exécuter quand même"** pour continuer.

### Option 2 — Depuis les sources

**Prérequis :** Python 3.10+

```bash
git clone https://github.com/TON_USERNAME/pc-tool.git
cd pc-tool
pip install -r requirements.txt
python timop.py
```

---

## 📋 Dépendances

```
customtkinter
psutil
pystray
Pillow
reportlab
```

Install en une commande :
```bash
pip install customtkinter psutil pystray Pillow reportlab
```

---

## 🔨 Compiler soi-même l'exécutable

1. Installe PyInstaller : `pip install pyinstaller`
2. Lance le script de build :
```bash
BUILD.bat
```
L'exécutable se trouve dans le dossier `dist/`.

---

## 🗂 Structure du projet

```
pc-tool/
├── timop.py          # Application principale
├── make_icon.py      # Génération de l'icône
├── BUILD.bat         # Script de compilation PyInstaller
├── installer.iss     # Script Inno Setup (installeur Windows)
├── icon.ico          # Icône de l'application
├── assets/           # Ressources graphiques
├── modules/          # Modules additionnels
└── requirements.txt  # Dépendances Python
```

---

## ⚙️ Configuration

Les paramètres sont sauvegardés dans :
```
%APPDATA%\PCTool\settings.json
```

Le journal des actions :
```
%APPDATA%\PCTool\historique.log
```

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

1. Fork le projet
2. Crée une branche : `git checkout -b feature/ma-fonctionnalite`
3. Commit : `git commit -m "Ajout de ma fonctionnalité"`
4. Push : `git push origin feature/ma-fonctionnalite`
5. Ouvre une **Pull Request**

Pour signaler un bug ou suggérer une fonctionnalité, ouvre une [**Issue**](../../issues).

---

## 📄 Licence

Ce projet est sous licence **MIT** — libre d'utilisation, de modification et de distribution.  
Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## ⚠️ Avertissement

PC Tool utilise des commandes système Windows (`sfc`, `DISM`, `netsh`, etc.).  
Certaines fonctionnalités nécessitent des **droits administrateur**.  
L'auteur ne peut être tenu responsable d'une mauvaise utilisation de l'outil.

---

*Développé avec ❤️ en Python*

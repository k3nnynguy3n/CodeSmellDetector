# 🛠️ Code Smell Detector & Refactoring Tool

This project was developed as part of the **CPSC 4260 - Refactoring and Software Design** course at Seattle University, Spring 2025.

## 📌 Overview
The goal of this individual project is to build a fully functional **Code Smell Detector and Refactoring Tool** with an interactive **Graphical User Interface (GUI)**. The tool allows users to upload a source code file and identifies the following code smells:

- **Long Method/Function**: Methods with 16+ lines (excluding blank lines).
- **Long Parameter List**: Functions with 4 or more parameters.
- **Duplicated Code**: Detected using **Jaccard Similarity** with a 0.75 threshold across functions.

## 💡 Features
- GUI-based interface for uploading and analyzing source code files.
- Automated detection of specified code smells.
- Optional refactoring support for duplicated code, producing a cleaned-up version of the file.
- Built with clean code principles, modular design, and extensibility in mind.

## 🧰 Tech Stack
- **Python 3.11+**
- **Tkinter** – for GUI interface
- **Standard Python Libraries**:
  - `re` – for regular expression-based parsing
  - `os` – for file handling
  - `tkinter.filedialog` – for file selection
  - `difflib` – for similarity comparisons

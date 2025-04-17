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

## 🚫 Limitations
- Only supports detection at the **function level** (not within individual functions like `main`).
- Does **not support lambda/anonymous functions**.
- **No AI or API-based analysis tools** were used as per project rules.

## 📁 Project Flow
1. Launch the application – GUI opens.
2. Upload a code file via GUI.
3. View alerts on any detected code smells.
4. Choose to refactor duplicated code (if found).
5. Save the refactored version.
6. Exit the program.

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ast
import threading
import os

class CodeSmellDetector:
    def __init__(self, code):
        self.code = code
        self.tree = ast.parse(code)
        self.issues = []

class CodeSmellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Smell Detector")
        self.create_widgets()

    def create_widgets(self):
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=("nsew"))

        self.load_button = ttk.Button(self.frame, text="Load Python File", command=self.load_file)
        self.load_button.grid(row=0, column=0, pady=10)

        self.results_text = tk.Text(self.frame, wrap="word", width=80, height=20)
        self.results_text.grid(row=1, column=0, pady=10)

        self.status_label = ttk.Label(self.frame, text="Status: Waiting for input")
        self.status_label.grid(row=2, column=0, pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, "r") as f:
                code = f.read()
            self.status_label.config(text="Analyzing file...")
            threading.Thread(target=self.analyze_code, args=(code,)).start()

    def analyze_code(self, code):
        detector = CodeSmellDetector(code)
        issues = detector.run_all_checks()

        self.results_text.delete("1.0", tk.END)
        if not issues:
            self.results_text.insert(tk.END, "No significant code smells detected.")
        else:
            for name, issue in issues:
                self.results_text.insert(tk.END, f"Function '{name}': {issue}\n")

        self.status_label.config(text="Analysis complete.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeSmellApp(root)
    root.mainloop()
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

    def run_all_checks(self):
        self.issues.clear()
        functions = [node for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef)]

        for func in functions:
            self.check_long_function(func)
            self.check_many_parameters(func)

        return self.issues

    def check_long_function(self, node):
        lines = [n.lineno for n in ast.walk(node) if hasattr(n, "lineno")]
        if lines:
            length = max(lines) - node.lineno
            if length > 15:
                self.issues.append((node.name, f"Long method/function: {length} lines"))

    def check_many_parameters(self, node):
        num_args = len(node.args.args)
        if num_args > 5:
            self.issues.append((node.name, f"Long parameters: {num_args}"))

class CodeSmellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Smell Detector")
        self.create_widgets()

    def create_widgets(self):
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)  

        self.load_button = ttk.Button(self.frame, text="Load Python File", command=self.load_file)
        self.load_button.grid(row=0, column=0, pady=10, sticky="n")

        self.results_text = tk.Text(self.frame, wrap="word")
        self.results_text.grid(row=1, column=0, sticky="nsew", pady=10)

        self.status_label = ttk.Label(self.frame, text="Status: Waiting for input")
        self.status_label.grid(row=2, column=0, pady=10, sticky="n")

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
    root.geometry("800x600")
    app = CodeSmellApp(root)
    root.mainloop()
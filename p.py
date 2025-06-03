import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ast
import threading
import re

class CodeSmellDetector:
    def __init__(self, code):
        self.code = code
        self.codeLines = code.splitlines()
        self.tree = ast.parse(code)
        self.issues = []

    def runAllChecks(self):
        self.issues.clear()
        functions = [node for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef)]

        for func in functions:
            self.checkLongFunction(func)
            self.checkManyParameters(func)

        self.checkDuplicateMethods(functions)
        return self.issues

    def checkLongFunction(self, node):
        longMethodThreshold = 15
        startLine = node.lineno - 1
        endLine = self.getEndLine(node)

        bodyLines = self.codeLines[startLine:endLine]
        nonBlankLines = [line for line in bodyLines if line.strip() != '']

        if len(nonBlankLines) > longMethodThreshold:
            self.issues.append((node.name, f"Long method/function: {len(nonBlankLines)} lines"))

    def getEndLine(self, node):
        allLines = [n.lineno for n in ast.walk(node) if hasattr(n, "lineno")]
        return max(allLines) if allLines else node.lineno

    def checkManyParameters(self, node):
        parameterLimit = 3
        numArgs = len(node.args.args)
        if numArgs > parameterLimit:
            self.issues.append((node.name, f"Long parameters: {numArgs} parameters"))

    def checkDuplicateMethods(self, functions):
        func_chars = []
        for node in functions:
            startLine = node.lineno - 1
            endLine = self.getEndLine(node)
            bodyLines = self.codeLines[startLine:endLine]
            code_block = "\n".join(bodyLines)
            # Exclude all whitespace characters before building the set
            non_whitespace_chars = [c for c in code_block if not c.isspace()]
            char_set = set(non_whitespace_chars)
            func_chars.append((node.name, char_set))

        threshold = 0.75
        n = len(func_chars)
        for i in range(n):
            name_i, chars_i = func_chars[i]
            for j in range(i + 1, n):
                name_j, chars_j = func_chars[j]
                if not chars_i and not chars_j:
                    continue
                intersection = chars_i.intersection(chars_j)
                union = chars_i.union(chars_j)
                similarity = len(intersection) / len(union) if union else 0
                if similarity >= threshold:
                    self.issues.append(
                        (f"{name_i} & {name_j}",
                         f"Duplicate code detected (character‐level similarity: {similarity:.2f})")
                    )

class CodeSmellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Smell Detector")
        self.createWidgets()

    def createWidgets(self):
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        self.loadButton = ttk.Button(self.frame, text="Load Python File", command=self.loadFile)
        self.loadButton.grid(row=0, column=0, pady=10, sticky="n")

        self.resultsText = tk.Text(self.frame, wrap="word", state="disabled")
        self.resultsText.grid(row=1, column=0, sticky="nsew", pady=10)

        self.statusLabel = ttk.Label(self.frame, text="Status: Waiting for input")
        self.statusLabel.grid(row=2, column=0, pady=10, sticky="n")

    def loadFile(self):
        filePath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if filePath:
            with open(filePath, "r") as f:
                code = f.read()
            self.statusLabel.config(text="Analyzing file...")
            threading.Thread(target=self.analyzeCode, args=(code,)).start()

    def analyzeCode(self, code):
        detector = CodeSmellDetector(code)
        issues = detector.runAllChecks()

        self.resultsText.config(state="normal")
        self.resultsText.delete("1.0", tk.END)

        if not issues:
            self.resultsText.insert(tk.END, "No significant code smells detected.")
        else:
            for name, issue in issues:
                self.resultsText.insert(tk.END, f"Function(s) '{name}': {issue}\n")

        self.resultsText.config(state="disabled")
        self.statusLabel.config(text="Analysis complete.")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = CodeSmellApp(root)
    root.mainloop()

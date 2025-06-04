import tkinter as tk
from tkinter import filedialog, ttk
import ast
import threading
import re

class CodeSmellDetector:
    def __init__(self, code):
        self.code = code
        self.codeLines = code.splitlines()
        self.tree = ast.parse(code)
        self.issues = []
        self.duplicatePairs = []  
    def runAllChecks(self):
        self.issues.clear()
        self.duplicatePairs.clear()
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
        funcChars = []
        for node in functions:
            startLine = node.lineno - 1
            endLine = self.getEndLine(node)
            bodyLines = self.codeLines[startLine:endLine]
            codeBlock = "\n".join(bodyLines)
            nonWhitespaceChars = [c for c in codeBlock if not c.isspace()]
            charSet = set(nonWhitespaceChars)
            funcChars.append((node, charSet))

        threshold = 0.75
        n = len(funcChars)
        for i in range(n):
            nodeI, charsI = funcChars[i]
            for j in range(i + 1, n):
                nodeJ, charsJ = funcChars[j]
                if not charsI and not charsJ:
                    continue
                intersection = charsI.intersection(charsJ)
                union = charsI.union(charsJ)
                similarity = len(intersection) / len(union) if union else 0
                if similarity >= threshold:
                    nameI = nodeI.name
                    nameJ = nodeJ.name
                    self.issues.append(
                        (f"{nameI} & {nameJ}",
                         f"Duplicate code detected (character-level similarity: {similarity:.2f})")
                    )
                    self.duplicatePairs.append((nodeI, nodeJ))

    def generateRefactoringSnippets(self):
        snippets = []
        for nodeI, nodeJ in self.duplicatePairs:
            argsI = [arg.arg for arg in nodeI.args.args]
            argsJ = [arg.arg for arg in nodeJ.args.args]
            if argsI != argsJ:
                snippets.append(None)
                continue
            params = argsI
            paramStr = ", ".join(params)
            startLineI = nodeI.lineno - 1
            endLineI = self.getEndLine(nodeI)
            bodyLines = self.codeLines[startLineI + 1:endLineI]
            cleanedBody = [line[4:] if line.startswith("    ") else line for line in bodyLines]

            extractedName = f"extracted{nodeI.name.capitalize()}{nodeJ.name.capitalize()}"
            extractedLines = [f"def {extractedName}({paramStr}):"]
            for line in cleanedBody:
                extractedLines.append(f"    {line}")
            extractedCode = "\n".join(extractedLines)

            callLine = f"return {extractedName}({paramStr})"
            funcILines = [f"def {nodeI.name}({paramStr}):", f"    {callLine}"]
            funcJLines = [f"def {nodeJ.name}({paramStr}):", f"    {callLine}"]
            snippet = "\n\n".join([extractedCode, "\n".join(funcILines), "\n".join(funcJLines)])
            snippets.append(snippet)
        return snippets

class CodeSmellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Smell Detector")
        self.currentDetector = None
        self.currentFilePath = None
        self.currentCode = None
        self.refactorFrame = None
        self.createWidgets()

    def createWidgets(self):
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=0)
        self.frame.rowconfigure(3, weight=0)

        self.loadButton = ttk.Button(self.frame, text="Load Python File", command=self.loadFile)
        self.loadButton.grid(row=0, column=0, pady=10, sticky="n")

        self.resultsText = tk.Text(self.frame, wrap="word", state="disabled", height=20)
        self.resultsText.grid(row=1, column=0, sticky="nsew", pady=10)

        self.statusLabel = ttk.Label(self.frame, text="Status: Waiting for input", anchor="center")
        self.statusLabel.grid(row=2, column=0, pady=10, sticky="n")

        self.refactorFrame = ttk.Frame(self.frame)
        self.refactorFrame.grid(row=3, column=0, sticky="ew", pady=5)
        self.refactorFrame.columnconfigure(0, weight=1)

    def loadFile(self):
        filePath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if not filePath:
            return

        with open(filePath, "r") as f:
            code = f.read()

        self.currentFilePath = filePath
        self.currentCode = code

        self.statusLabel.config(text="Status: Analyzing file...")
        threading.Thread(target=self.analyzeCode, args=(filePath, code)).start()

    def analyzeCode(self, filePath, code):
        detector = CodeSmellDetector(code)
        issues = detector.runAllChecks()

        self.currentDetector = detector
        self.root.after(0, lambda: self.displayResults(issues))

    def displayResults(self, issues):
        self.resultsText.config(state="normal")
        self.resultsText.delete("1.0", tk.END)
        for widget in self.refactorFrame.winfo_children():
            widget.destroy()

        if not issues:
            self.resultsText.insert(tk.END, "No significant code smells detected.\n")
        else:
            for name, issue in issues:
                self.resultsText.insert(tk.END, f"Function(s) '{name}': {issue}\n")

            if self.currentDetector.duplicatePairs:
                prompt = ttk.Label(self.refactorFrame, text="Duplicated code detected. Refactor and save new file?")
                prompt.grid(row=0, column=0, pady=(5, 0))
                refactorBtn = ttk.Button(self.refactorFrame, text="Refactor", command=self.onRefactorClicked)
                refactorBtn.grid(row=1, column=0, pady=(5, 0))

        self.resultsText.config(state="disabled")
        self.statusLabel.config(text="Status: Analysis complete.")

    def onRefactorClicked(self):
        self.createRefactoredFile(self.currentFilePath, self.currentCode, self.currentDetector)

    def createRefactoredFile(self, originalPath, originalCode, detector):
        snippets = detector.generateRefactoringSnippets()
        lines = originalCode.splitlines()
        newLines = list(lines)

        replacements = []
        for index, (nodeI, nodeJ) in enumerate(detector.duplicatePairs):
            snippet = snippets[index]
            if snippet is None:
                continue

            startI = nodeI.lineno - 1
            endI = detector.getEndLine(nodeI)
            startJ = nodeJ.lineno - 1
            endJ = detector.getEndLine(nodeJ)

            snippetLines = snippet.splitlines()
            replacements.append((startI, endI, snippetLines))
            replacements.append((startJ, endJ, []))

        replacements.sort(key=lambda x: x[0], reverse=True)
        for start, end, snippetLines in replacements:
            newLines[start:end] = snippetLines

        savePath = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py")],
            initialfile=f"refactored_{originalPath.split('/')[-1]}"
        )
        if not savePath:
            return

        with open(savePath, "w") as outFile:
            outFile.write("\n".join(newLines))

        self.resultsText.config(state="normal")
        self.resultsText.insert(tk.END, f"\nRefactored code saved to: {savePath}\n")
        self.resultsText.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = CodeSmellApp(root)
    root.mainloop()

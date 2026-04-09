import tkinter as tk
from tkinter import messagebox
import time
import math
import operator

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern BitWise Calculator")
        self.root.geometry("420x650")
        self.root.resizable(False, False)

        # Portable Font Stack
        self.font_main = ("Helvetica", 14)
        self.font_bold = ("Helvetica", 36, "bold")
        self.font_small = ("Helvetica", 10)
        self.font_history = ("Helvetica", 12)

        # Themes Configuration
        self.themes = {
            "light": {
                "bg": "#F0F0F0",
                "display_bg": "#FFFFFF",
                "text": "#000000",
                "btn_num": "#FFFFFF",
                "btn_op": "#E0E0E0",
                "btn_accent": "#0078D7",
                "btn_accent_text": "#FFFFFF",
                "btn_hover": "#D0D0D0"
            },
            "dark": {
                "bg": "#1A1A1A",
                "display_bg": "#252525",
                "text": "#FFFFFF",
                "btn_num": "#333333",
                "btn_op": "#2B2B2B",
                "btn_accent": "#4CC2FF",
                "btn_accent_text": "#000000",
                "btn_hover": "#404040"
            }
        }
        self.current_theme_name = "dark"
        self.expression = ""
        
        self.setup_ui()
        self.apply_theme()
        self.update_clock()
        self.setup_bindings()

    def setup_ui(self):
        # Top Bar (Clock and Theme Toggle)
        self.top_bar = tk.Frame(self.root, height=40, padx=10)
        self.top_bar.pack(fill="x", side="top")
        
        self.clock_label = tk.Label(self.top_bar, font=self.font_small)
        self.clock_label.pack(side="left")
        
        self.theme_btn = tk.Button(self.top_bar, text="Switch Theme", command=self.toggle_theme, 
                                 relief="flat", font=self.font_small)
        self.theme_btn.pack(side="right")

        # Display Area
        self.display_frame = tk.Frame(self.root, padx=20, pady=20)
        self.display_frame.pack(fill="x")
        
        self.history_label = tk.Label(self.display_frame, text="", anchor="e", font=self.font_history)
        self.history_label.pack(fill="x")
        
        self.result_var = tk.StringVar(value="0")
        self.display_label = tk.Label(self.display_frame, textvariable=self.result_var, 
                                    anchor="e", font=self.font_bold)
        self.display_label.pack(fill="x")

        self.grid_frame = tk.Frame(self.root, padx=10, pady=10)
        self.grid_frame.pack(fill="both", expand=True)

        buttons = [
            ('~', 0, 0, 'bitwise'), ('<<', 0, 1, 'bitwise'), ('>>', 0, 2, 'bitwise'), ('C', 0, 3, 'action'),
            ('&', 1, 0, 'bitwise'), ('|', 1, 1, 'bitwise'), ('^', 1, 2, 'bitwise'), ('/', 1, 3, 'op'),
            ('7', 2, 0, 'num'), ('8', 2, 1, 'num'), ('9', 2, 2, 'num'), ('*', 2, 3, 'op'),
            ('4', 3, 0, 'num'), ('5', 3, 1, 'num'), ('6', 3, 2, 'num'), ('-', 3, 3, 'op'),
            ('1', 4, 0, 'num'), ('2', 4, 1, 'num'), ('3', 4, 2, 'num'), ('+', 4, 3, 'op'),
            ('+/-', 5, 0, 'num'), ('0', 5, 1, 'num'), ('.', 5, 2, 'num'), ('=', 5, 3, 'equal')
        ]

        self.btns = {}
        for (text, r, c, btype) in buttons:
            btn = tk.Button(self.grid_frame, text=text, width=5, height=2, 
                           font=self.font_main, relief="flat",
                           command=lambda t=text: self.on_click(t))
            btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
            self.btns[text] = (btn, btype)
            
        for i in range(6): self.grid_frame.rowconfigure(i, weight=1)
        for i in range(4): self.grid_frame.columnconfigure(i, weight=1)

    def apply_theme(self):
        t = self.themes[self.current_theme_name]
        self.root.configure(bg=t["bg"])
        self.top_bar.configure(bg=t["bg"])
        self.clock_label.configure(bg=t["bg"], fg=t["text"])
        self.theme_btn.configure(bg=t["bg"], fg=t["text"], activebackground=t["btn_hover"])
        
        self.display_frame.configure(bg=t["bg"])
        self.history_label.configure(bg=t["bg"], fg=t["text"])
        self.display_label.configure(bg=t["bg"], fg=t["text"])
        
        self.grid_frame.configure(bg=t["bg"])
        
        for text, (btn, btype) in self.btns.items():
            if btype == 'num':
                bg, fg = t["btn_num"], t["text"]
            elif btype == 'op' or btype == 'bitwise':
                bg, fg = t["btn_op"], t["text"]
            elif btype == 'action':
                bg, fg = t["btn_op"], "#FF4D4D" # Red for clear
            elif btype == 'equal':
                bg, fg = t["btn_accent"], t["btn_accent_text"]
            
            btn.configure(bg=bg, fg=fg, activebackground=t["btn_hover"], activeforeground=fg)

    def toggle_theme(self):
        self.current_theme_name = "light" if self.current_theme_name == "dark" else "dark"
        self.apply_theme()

    def update_clock(self):
        now = time.strftime("%H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self.update_clock)

    def on_click(self, char):
        if char == 'C':
            self.expression = ""
            self.history_label.config(text="")
            self.result_var.set("0")
        elif char == '=':
            self.calculate()
        elif char == '+/-':
            if self.expression.startswith('-'):
                self.expression = self.expression[1:]
            else:
                self.expression = '-' + self.expression
            self.result_var.set(self.expression or "0")
        elif char == '~':
            try:
                val = int(eval(self.expression or "0"))
                self.expression = str(~val)
                self.result_var.set(self.expression)
            except:
                self.result_var.set("Error")
        else:
            mapping = {'&': '&', '|': '|', '^': '^', '<<': '<<', '>>': '>>'}
            self.expression += mapping.get(char, char)
            self.result_var.set(self.expression)

    def calculate(self):
        try:
            expr = self.expression
            if not expr: return
            result = eval(expr)
            self.history_label.config(text=f"{expr} =")
            self.result_var.set(str(result))
            self.expression = str(result)
        except Exception as e:
            messagebox.showerror("Error", "Invalid Expression")
            self.expression = ""
            self.result_var.set("Error")

    def setup_bindings(self):
        self.root.bind('<Key>', self.handle_keypress)
        self.root.bind('<Return>', lambda e: self.calculate())
        self.root.bind('<BackSpace>', self.handle_backspace)
        self.root.bind('<Escape>', lambda e: self.on_click('C'))

    def handle_keypress(self, event):
        char = event.char
        if char in "0123456789+-*/.&|^":
            self.on_click(char)
        elif char == '<':
             self.on_click('<<')
        elif char == '>':
             self.on_click('>>')

    def handle_backspace(self, event):
        self.expression = self.expression[:-1]
        self.result_var.set(self.expression or "0")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()

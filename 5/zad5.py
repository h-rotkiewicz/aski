import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class CPU:
    def __init__(self):
        self.reset()

    def reset(self):
        self.reg16 = {
            "AX": 0,
            "BX": 0,
            "CX": 0,
            "DX": 0
        }

    def is_reg16(self, name):
        return name in self.reg16

    def is_reg8(self, name):
        return name in {"AH", "AL", "BH", "BL", "CH", "CL", "DH", "DL"}

    def is_register(self, name):
        return self.is_reg16(name) or self.is_reg8(name)

    def get_value(self, name):
        name = name.upper()

        if self.is_reg16(name):
            return self.reg16[name]

        if self.is_reg8(name):
            base = name[0] + "X"
            full = self.reg16[base]

            if name[1] == "H":
                return (full >> 8) & 0xFF
            else:
                return full & 0xFF

        raise ValueError(f"Nieznany rejestr: {name}")

    def set_value(self, name, value):
        name = name.upper()

        if self.is_reg16(name):
            self.reg16[name] = value % 65536
            return

        if self.is_reg8(name):
            base = name[0] + "X"
            full = self.reg16[base]
            value = value % 256

            if name[1] == "H":
                low = full & 0x00FF
                self.reg16[base] = ((value << 8) | low) % 65536
            else:
                high = full & 0xFF00
                self.reg16[base] = (high | value) % 65536
            return

        raise ValueError(f"Nieznany rejestr: {name}")

    def operand_size(self, operand):
        operand = operand.upper()
        if self.is_reg16(operand):
            return 16
        if self.is_reg8(operand):
            return 8
        raise ValueError(f"Operand nie jest rejestrem: {operand}")


class Instruction:
    def __init__(self, opcode, op1, op2, raw_line, line_no):
        self.opcode = opcode.upper()
        self.op1 = op1.upper()
        self.op2 = op2.upper()
        self.raw_line = raw_line
        self.line_no = line_no


class ProgramParser:
    VALID_OPCODES = {"MOV", "ADD", "SUB"}

    @staticmethod
    def parse_number(text):
        text = text.strip()

        # liczby dziesiętne
        if text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
            return int(text)

        # liczby szesnastkowe, np. 0xFF
        if text.lower().startswith("0x"):
            return int(text, 16)

        raise ValueError(f"Niepoprawna liczba: {text}")

    @staticmethod
    def is_immediate(token):
        try:
            ProgramParser.parse_number(token)
            return True
        except Exception:
            return False

    @staticmethod
    def clean_line(line):
        # usuwanie komentarza po ;
        if ";" in line:
            line = line.split(";", 1)[0]
        return line.strip()

    @staticmethod
    def parse(program_text):
        instructions = []
        lines = program_text.splitlines()

        for idx, raw in enumerate(lines, start=1):
            cleaned = ProgramParser.clean_line(raw)

            if not cleaned:
                continue

            parts = cleaned.split(None, 1)
            if len(parts) < 2:
                raise ValueError(f"Linia {idx}: niepełna instrukcja.")

            opcode = parts[0].upper()
            if opcode not in ProgramParser.VALID_OPCODES:
                raise ValueError(f"Linia {idx}: nieznana instrukcja '{opcode}'.")

            args_part = parts[1]
            args = [a.strip() for a in args_part.split(",")]

            if len(args) != 2:
                raise ValueError(f"Linia {idx}: instrukcja musi mieć 2 argumenty.")

            op1, op2 = args[0], args[1]

            instructions.append(Instruction(opcode, op1, op2, raw, idx))

        return instructions


class ExecutionEngine:
    def __init__(self, cpu):
        self.cpu = cpu

    def get_operand_value(self, operand):
        operand = operand.upper()

        if self.cpu.is_register(operand):
            return self.cpu.get_value(operand)

        if ProgramParser.is_immediate(operand):
            return ProgramParser.parse_number(operand)

        raise ValueError(f"Niepoprawny operand: {operand}")

    def execute(self, instr):
        opcode = instr.opcode
        dst = instr.op1
        src = instr.op2

        if not self.cpu.is_register(dst):
            raise ValueError(
                f"Linia {instr.line_no}: pierwszy operand musi być rejestrem."
            )

        dst_size = self.cpu.operand_size(dst)
        src_value = self.get_operand_value(src)

        if self.cpu.is_register(src):
            src_size = self.cpu.operand_size(src)
            if src_size != dst_size:
                raise ValueError(
                    f"Linia {instr.line_no}: niezgodny rozmiar operandów ({dst} i {src})."
                )
        else:
            
            if dst_size == 8 and not (-255 <= src_value <= 255 or 0 <= src_value <= 255):
                pass  
            if dst_size == 16 and not (-65535 <= src_value <= 65535 or 0 <= src_value <= 65535):
                pass  

        current = self.cpu.get_value(dst)

        if opcode == "MOV":
            result = src_value
        elif opcode == "ADD":
            result = current + src_value
        elif opcode == "SUB":
            result = current - src_value
        else:
            raise ValueError(f"Linia {instr.line_no}: nieobsługiwana instrukcja '{opcode}'.")

        self.cpu.set_value(dst, result)

# GUI
class CPUSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Symulator prostego procesora")
        self.root.geometry("1200x760")
        self.root.minsize(1050, 700)

        self.cpu = CPU()
        self.engine = ExecutionEngine(self.cpu)

        self.instructions = []
        self.current_index = 0
        self.program_loaded = False

        self.build_ui()
        self.refresh_registers()
        self.refresh_state()

    def build_ui(self):
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 10))
        style.configure("TLabelframe.Label", font=("Arial", 12, "bold"))

        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        # LEWA CZĘŚĆ - PROGRAM
        left = ttk.LabelFrame(main, text="Program", padding=10)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ttk.Label(left, text="Wpisz program asemblerowy:").pack(anchor="w")

        self.program_text = scrolledtext.ScrolledText(
            left, wrap="none", font=("Consolas", 11), height=25
        )
        self.program_text.pack(fill="both", expand=True, pady=(5, 10))

        sample = (
            "MOV AX, 10\n"
            "MOV BX, 5\n"
            "ADD AX, BX\n"
            "MOV CL, 3\n"
            "ADD AL, CL\n"
            "SUB AX, 1\n"
            "; komentarz\n"
        )
        self.program_text.insert("1.0", sample)

        buttons_program = ttk.Frame(left)
        buttons_program.pack(fill="x", pady=(5, 5))

        ttk.Button(buttons_program, text="Załaduj program", command=self.load_program).pack(side="left", padx=3)
        ttk.Button(buttons_program, text="Uruchom całość", command=self.run_all).pack(side="left", padx=3)
        ttk.Button(buttons_program, text="Krok", command=self.run_step).pack(side="left", padx=3)
        ttk.Button(buttons_program, text="Reset CPU", command=self.reset_cpu).pack(side="left", padx=3)
        ttk.Button(buttons_program, text="Reset programu", command=self.reset_program_execution).pack(side="left", padx=3)

        file_buttons = ttk.Frame(left)
        file_buttons.pack(fill="x", pady=(5, 5))

        ttk.Button(file_buttons, text="Zapisz do pliku", command=self.save_program_to_file).pack(side="left", padx=3)
        ttk.Button(file_buttons, text="Wczytaj z pliku", command=self.load_program_from_file).pack(side="left", padx=3)

        ttk.Label(left, text="Lista instrukcji po sparsowaniu:").pack(anchor="w", pady=(10, 0))

        self.instructions_list = tk.Listbox(left, font=("Consolas", 11), height=12)
        self.instructions_list.pack(fill="both", expand=True, pady=(5, 0))

        #REJESTRY I STAN
        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=False, padx=(5, 0))

        reg_frame = ttk.LabelFrame(right, text="Rejestry", padding=10)
        reg_frame.pack(fill="x", pady=(0, 10))

        self.reg_labels = {}

        ttk.Label(reg_frame, text="Rejestr", width=8).grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(reg_frame, text="DEC", width=10).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(reg_frame, text="HEX", width=10).grid(row=0, column=2, padx=5, pady=2)

        row = 1
        for reg in ["AX", "AH", "AL", "BX", "BH", "BL", "CX", "CH", "CL", "DX", "DH", "DL"]:
            ttk.Label(reg_frame, text=reg, width=8).grid(row=row, column=0, padx=5, pady=2)

            dec_label = ttk.Label(reg_frame, text="0", width=10)
            dec_label.grid(row=row, column=1, padx=5, pady=2)

            hex_label = ttk.Label(reg_frame, text="0x00", width=10)
            hex_label.grid(row=row, column=2, padx=5, pady=2)

            self.reg_labels[reg] = (dec_label, hex_label)
            row += 1

        state_frame = ttk.LabelFrame(right, text="Stan wykonania", padding=10)
        state_frame.pack(fill="x", pady=(0, 10))

        self.status_var = tk.StringVar(value="Program niezaładowany.")
        self.current_instr_var = tk.StringVar(value="Bieżąca instrukcja: brak")
        self.next_instr_var = tk.StringVar(value="Następna instrukcja: brak")

        ttk.Label(state_frame, textvariable=self.status_var, wraplength=320).pack(anchor="w", pady=3)
        ttk.Label(state_frame, textvariable=self.current_instr_var, wraplength=320).pack(anchor="w", pady=3)
        ttk.Label(state_frame, textvariable=self.next_instr_var, wraplength=320).pack(anchor="w", pady=3)

        log_frame = ttk.LabelFrame(right, text="Log", padding=10)
        log_frame.pack(fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame, wrap="word", font=("Consolas", 10), height=18, state="disabled"
        )
        self.log_text.pack(fill="both", expand=True)



    def log(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")


    def refresh_registers(self):
        for reg in ["AX", "BX", "CX", "DX", "AH", "AL", "BH", "BL", "CH", "CL", "DH", "DL"]:
            value = self.cpu.get_value(reg)

            if reg in {"AX", "BX", "CX", "DX"}:
                hex_text = f"0x{value:04X}"
            else:
                hex_text = f"0x{value:02X}"

            dec_label, hex_label = self.reg_labels[reg]
            dec_label.config(text=str(value))
            hex_label.config(text=hex_text)

    def refresh_state(self):
        if not self.program_loaded:
            self.status_var.set("Program niezaładowany.")
            self.current_instr_var.set("Bieżąca instrukcja: brak")
            self.next_instr_var.set("Następna instrukcja: brak")
            self.instructions_list.selection_clear(0, tk.END)
            return

        if self.current_index >= len(self.instructions):
            self.status_var.set("Program załadowany. Wykonanie zakończone.")
            self.current_instr_var.set("Bieżąca instrukcja: brak")
            self.next_instr_var.set("Następna instrukcja: brak")
            self.instructions_list.selection_clear(0, tk.END)
            return

        self.status_var.set(f"Program załadowany. Liczba instrukcji: {len(self.instructions)}")
        current = self.instructions[self.current_index]
        self.current_instr_var.set(
            f"Bieżąca instrukcja: #{self.current_index + 1} (linia źródłowa {current.line_no}) -> {current.raw_line.strip()}"
        )

        if self.current_index + 1 < len(self.instructions):
            nxt = self.instructions[self.current_index + 1]
            self.next_instr_var.set(
                f"Następna instrukcja: #{self.current_index + 2} (linia źródłowa {nxt.line_no}) -> {nxt.raw_line.strip()}"
            )
        else:
            self.next_instr_var.set("Następna instrukcja: brak")

        self.instructions_list.selection_clear(0, tk.END)
        self.instructions_list.selection_set(self.current_index)
        self.instructions_list.see(self.current_index)


    def load_program(self):
        program = self.program_text.get("1.0", "end-1c")

        try:
            instructions = ProgramParser.parse(program)
            if not instructions:
                messagebox.showwarning("Brak programu", "Program nie zawiera żadnych instrukcji.")
                return

            self.instructions = instructions
            self.current_index = 0
            self.program_loaded = True

            self.instructions_list.delete(0, tk.END)
            for i, instr in enumerate(self.instructions, start=1):
                self.instructions_list.insert(
                    tk.END,
                    f"{i:03d}. [linia {instr.line_no}] {instr.opcode} {instr.op1}, {instr.op2}"
                )

            self.log("Program został poprawnie załadowany.")
            self.refresh_state()
        except Exception as e:
            messagebox.showerror("Błąd parsowania", str(e))

    def run_step(self):
        if not self.program_loaded:
            messagebox.showwarning("Brak programu", "Najpierw załaduj program.")
            return

        if self.current_index >= len(self.instructions):
            messagebox.showinfo("Koniec", "Program został już wykonany.")
            return

        instr = self.instructions[self.current_index]

        try:
            self.log(f"Wykonywanie kroku #{self.current_index + 1}: {instr.raw_line.strip()}")
            self.engine.execute(instr)
            self.current_index += 1
            self.refresh_registers()
            self.refresh_state()

            if self.current_index >= len(self.instructions):
                self.log("Wykonanie programu zakończone.")
        except Exception as e:
            messagebox.showerror("Błąd wykonania", str(e))
            self.log(f"BŁĄD: {e}")

    def run_all(self):
        if not self.program_loaded:
            messagebox.showwarning("Brak programu", "Najpierw załaduj program.")
            return

        if self.current_index >= len(self.instructions):
            messagebox.showinfo("Koniec", "Program został już wykonany.")
            return

        try:
            while self.current_index < len(self.instructions):
                instr = self.instructions[self.current_index]
                self.log(f"Wykonywanie kroku #{self.current_index + 1}: {instr.raw_line.strip()}")
                self.engine.execute(instr)
                self.current_index += 1

            self.refresh_registers()
            self.refresh_state()
            self.log("Wykonanie całego programu zakończone.")
            messagebox.showinfo("Gotowe", "Program został wykonany w trybie całościowym.")
        except Exception as e:
            self.refresh_registers()
            self.refresh_state()
            messagebox.showerror("Błąd wykonania", str(e))
            self.log(f"BŁĄD: {e}")

    def reset_cpu(self):
        self.cpu.reset()
        self.refresh_registers()
        self.log("Zresetowano rejestry procesora.")

    def reset_program_execution(self):
        self.current_index = 0
        self.refresh_state()
        self.log("Zresetowano licznik wykonania programu.")


    def save_program_to_file(self):
        content = self.program_text.get("1.0", "end-1c")

        path = filedialog.asksaveasfilename(
            title="Zapisz program",
            defaultextension=".asm",
            filetypes=[("Pliki ASM", "*.asm"), ("Pliki tekstowe", "*.txt"), ("Wszystkie pliki", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Zapisano", "Program został zapisany do pliku.")
            self.log(f"Zapisano program do pliku: {path}")
        except Exception as e:
            messagebox.showerror("Błąd zapisu", str(e))

    def load_program_from_file(self):
        path = filedialog.askopenfilename(
            title="Wczytaj program",
            filetypes=[("Pliki ASM", "*.asm"), ("Pliki tekstowe", "*.txt"), ("Wszystkie pliki", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            self.program_text.delete("1.0", "end")
            self.program_text.insert("1.0", content)

            self.log(f"Wczytano program z pliku: {path}")
            messagebox.showinfo("Wczytano", "Program został wczytany z pliku.")
        except Exception as e:
            messagebox.showerror("Błąd odczytu", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSimulatorApp(root)
    root.mainloop()
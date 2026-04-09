import tkinter as tk
from tkinter import messagebox
import time
import random
import statistics
import subprocess


class ReactionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Psychomotor Reaction Timer")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        self.all_results = []  # Stores (test_name, time, correct)

        self.current_frame = None
        self.show_menu()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_menu(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.current_frame.pack(expand=True, fill='both')

        tk.Label(self.current_frame, text="Psychomotor Reaction Test",
                 font=("Arial", 28, "bold"), bg="#f0f0f0").pack(pady=80)
        tk.Label(self.current_frame, text="Measure your reaction speed to visual and auditory stimuli.", font=(
            "Arial", 14), bg="#f0f0f0").pack(pady=10)

        start_btn = tk.Button(self.current_frame, text="START TEST SEQUENCE", font=("Arial", 16, "bold"),
                              command=self.start_sequence, bg="#4CAF50", fg="white", padx=20, pady=10)
        start_btn.pack(pady=50)

    def start_sequence(self):
        # Sequence: (Test Type, Is Practice)
        self.sequence = [
            ("Simple Visual", True),
            ("Simple Visual", False),
            ("Choice Visual", True),
            ("Choice Visual", False),
            ("Simple Auditory", True),
            ("Simple Auditory", False)
        ]
        self.seq_idx = 0
        self.run_next_in_sequence()

    def run_next_in_sequence(self):
        if self.seq_idx < len(self.sequence):
            test_type, is_practice = self.sequence[self.seq_idx]
            self.seq_idx += 1
            self.show_instructions(test_type, is_practice)
        else:
            self.show_results()

    def show_instructions(self, test_type, is_practice):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.current_frame.pack(expand=True, fill='both')

        title = f"{test_type} - {'PRACTICE' if is_practice else 'TEST'}"
        tk.Label(self.current_frame, text=title, font=(
            "Arial", 24, "bold"), bg="#f0f0f0", fg="#333").pack(pady=40)

        instr_text = ""
        if test_type == "Simple Visual":
            instr_text = "Wait for the screen to turn RED.\nPress SPACE as fast as you can when it does."
        elif test_type == "Choice Visual":
            instr_text = "Wait for a colored square to appear.\nPress 'R' for RED and 'G' for GREEN."
        elif test_type == "Simple Auditory":
            instr_text = "Wait for a sound to play.\nPress SPACE as fast as you can when you hear it."

        tk.Label(self.current_frame, text=instr_text, font=(
            "Arial", 16), bg="#f0f0f0", justify="center").pack(pady=20)

        if is_practice:
            tk.Label(self.current_frame, text="Practice results are not recorded.", font=(
                "Arial", 12, "italic"), bg="#f0f0f0", fg="gray").pack(pady=10)

        btn_text = "START PRACTICE" if is_practice else "START REAL TEST"
        start_btn = tk.Button(self.current_frame, text=btn_text, font=("Arial", 14),
                              command=lambda: self.run_test(test_type, is_practice), bg="#2196F3", fg="white", padx=15, pady=5)
        start_btn.pack(pady=30)

    def run_test(self, test_type, is_practice):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg="white")
        self.current_frame.pack(expand=True, fill='both')
        self.root.focus_set()

        # Bind ESC to return to menu
        self.root.bind("<Escape>", lambda e: self.show_menu())

        self.trials_left = 2 if is_practice else 5
        self.current_results = []
        self.test_type = test_type
        self.is_practice = is_practice

        self.next_trial()

    def next_trial(self):
        if self.trials_left > 0:
            self.trials_left -= 1
            self.current_frame.configure(bg="white")
            for widget in self.current_frame.winfo_children():
                widget.destroy()

            self.trial_active = False
            self.stimulus_triggered = False

            self.root.bind("<space>", self.on_premature_press)
            self.root.bind("<r>", self.on_premature_press)
            self.root.bind("<g>", self.on_premature_press)

            delay = random.randint(500, 2000)
            self.after_id = self.root.after(delay, self.trigger_stimulus)
        else:
            self.root.unbind("<Escape>")
            if not self.is_practice:
                self.all_results.extend(
                    [(self.test_type, r[0], r[1]) for r in self.current_results])
            self.run_next_in_sequence()

    def on_premature_press(self, event):
        if not self.stimulus_triggered:
            if hasattr(self, "after_id"):
                self.root.after_cancel(self.after_id)

            self.root.unbind("<space>")
            self.root.unbind("<r>")
            self.root.unbind("<g>")

            for widget in self.current_frame.winfo_children():
                widget.destroy()

            tk.Label(self.current_frame, text="TOO EARLY!", font=(
                "Arial", 30, "bold"), fg="orange", bg="white").pack(expand=True)
            self.root.after(400, self.next_trial)  # Very fast feedback

    def trigger_stimulus(self):
        self.start_time = time.perf_counter()
        self.trial_active = True
        self.stimulus_triggered = True

        self.root.unbind("<space>")
        self.root.unbind("<r>")
        self.root.unbind("<g>")

        if self.test_type == "Simple Visual":
            self.current_frame.configure(bg="red")
            self.root.bind("<space>", self.on_key)

        elif self.test_type == "Choice Visual":
            self.target_color = random.choice(["red", "green"])
            canvas = tk.Canvas(self.current_frame, width=200,
                               height=200, bg="white", highlightthickness=0)
            canvas.pack(expand=True)
            canvas.create_rectangle(0, 0, 200, 200, fill=self.target_color)
            self.root.bind("<r>", lambda e: self.on_key(e, "red"))
            self.root.bind("<g>", lambda e: self.on_key(e, "green"))
            self.root.bind("<space>", lambda e: self.on_key(e, "wrong"))

        elif self.test_type == "Simple Auditory":
            try:
                subprocess.Popen(
                    ["paplay", "/usr/share/sounds/ocean/stereo/bell.oga"], stderr=subprocess.DEVNULL)
            except:
                try:
                    subprocess.Popen(
                        ["bash", "-c", "echo -e '\a'"], stderr=subprocess.DEVNULL)
                except:
                    pass
            self.root.bind("<space>", self.on_key)

    def on_key(self, event, choice=None):
        if not self.trial_active:
            return

        reaction_time = (time.perf_counter() - self.start_time) * 1000  # ms
        self.trial_active = False
        self.root.unbind("<space>")
        self.root.unbind("<r>")
        self.root.unbind("<g>")

        correct = True
        if self.test_type == "Choice Visual":
            if choice != self.target_color:
                correct = False

        self.current_results.append((reaction_time, correct))

        color = "green" if correct else "red"
        msg = f"{int(reaction_time)} ms" if correct else "WRONG!"

        feedback_label = tk.Label(self.current_frame, text=msg, font=(
            "Arial", 30, "bold"), fg=color, bg="white")
        feedback_label.pack(expand=True)

        self.root.after(400, self.next_trial)

    def show_results(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.current_frame.pack(expand=True, fill='both')

        tk.Label(self.current_frame, text="TEST RESULTS", font=(
            "Arial", 28, "bold"), bg="#f0f0f0").pack(pady=30)

        # Process results
        unique_tests = sorted(list(set(r[0] for r in self.all_results)))

        results_container = tk.Frame(self.current_frame, bg="#f0f0f0")
        results_container.pack(pady=10)

        for test_name in unique_tests:
            test_data = [r for r in self.all_results if r[0] == test_name]
            times = [r[1] for r in test_data if r[2]]  # Correct only for mean
            correct_count = sum(1 for r in test_data if r[2])
            error_count = len(test_data) - correct_count
            avg_time = statistics.mean(times) if times else 0

            test_frame = tk.Frame(
                results_container, bg="white", padx=10, pady=10, relief="groove", borderwidth=1)
            test_frame.pack(pady=5, fill="x")

            header = f"{test_name}: Avg {int(avg_time)}ms | Correct: {
                correct_count} | Errors: {error_count}"
            tk.Label(test_frame, text=header, font=(
                "Arial", 12, "bold"), bg="white").pack(anchor="w")

        tk.Button(self.current_frame, text="BACK TO MENU",
                  command=self.show_menu, font=("Arial", 12)).pack(pady=30)


if __name__ == "__main__":
    root = tk.Tk()
    app = ReactionApp(root)
    root.mainloop()

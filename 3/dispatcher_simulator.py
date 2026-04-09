import tkinter as tk
from tkinter import messagebox, ttk
import psutil
import random
import time
import threading


class DispatcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title(
            "Symulator Stanowiska Dyspozytorskiego Linii Produkcyjnej")
        self.root.geometry("900x700")

        self.logged_in = False
        self.operator_present = True
        self.last_operator_check = time.time()
        self.check_active = False
        self.production_running = True

        self.motor_temp = 40.0
        self.production_speed = 100
        self.fan_active = False
        self.emergency_stop = False

        self.style = ttk.Style()
        self.style.configure("Alarm.TLabel", foreground="red",
                             font=("Helvetica", 12, "bold"))
        self.style.configure("Normal.TLabel", font=("Helvetica", 10))
        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))

        self.setup_login()

    def setup_login(self):
        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(self.login_frame, text="Logowanie Operatora", font=(
            "Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        ttk.Label(self.login_frame, text="Użytkownik:").grid(
            row=1, column=0, sticky="e", pady=5)
        self.user_entry = ttk.Entry(self.login_frame)
        self.user_entry.grid(row=1, column=1, pady=5)
        self.user_entry.insert(0, "operator1")

        ttk.Label(self.login_frame, text="Hasło:").grid(
            row=2, column=0, sticky="e", pady=5)
        self.pass_entry = ttk.Entry(self.login_frame, show="*")
        self.pass_entry.grid(row=2, column=1, pady=5)
        self.pass_entry.insert(0, "admin")

        ttk.Button(self.login_frame, text="Zaloguj", command=self.login).grid(
            row=3, column=0, columnspan=2, pady=20)

    def login(self):
        user = self.user_entry.get()
        password = self.pass_entry.get()

        if user and password:
            self.logged_in = True
            self.login_frame.destroy()
            self.setup_main_dashboard()
            self.start_simulation()
            self.schedule_operator_check()
        else:
            messagebox.showerror("Błąd", "Nieprawidłowe dane logowania")

    def setup_main_dashboard(self):
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.pack(fill="both", expand=True)

        header = ttk.Label(
            self.main_container, text="PANEL NADZORU LINII PRODUKCYJNEJ", style="Header.TLabel")
        header.pack(pady=10)

        top_panels = ttk.Frame(self.main_container)
        top_panels.pack(fill="x", pady=10)

        self.pc_frame = ttk.LabelFrame(
            top_panels, text="Diagnostyka Systemu (PC)", padding="10")
        self.pc_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.cpu_usage_label = ttk.Label(self.pc_frame, text="Użycie CPU: --%")
        self.cpu_usage_label.pack(anchor="w")

        self.cpu_temp_label = ttk.Label(self.pc_frame, text="Temp. CPU: --°C")
        self.cpu_temp_label.pack(anchor="w")

        self.mem_usage_label = ttk.Label(self.pc_frame, text="Użycie RAM: --%")
        self.mem_usage_label.pack(anchor="w")

        self.prod_frame = ttk.LabelFrame(
            top_panels, text="Parametry Linii Produkcyjnej", padding="10")
        self.prod_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.motor_temp_label = ttk.Label(
            self.prod_frame, text="Temp. Silnika: --°C")
        self.motor_temp_label.pack(anchor="w")

        self.speed_label = ttk.Label(
            self.prod_frame, text="Prędkość Linii: 100%")
        self.speed_label.pack(anchor="w")

        self.fan_status_label = ttk.Label(
            self.prod_frame, text="Wentylator Pomocniczy: WYŁ", foreground="gray")
        self.fan_status_label.pack(anchor="w")

        log_frame = ttk.LabelFrame(
            self.main_container, text="Dziennik Zdarzeń i Komunikaty", padding="10")
        log_frame.pack(fill="both", expand=True, pady=10)

        self.log_text = tk.Text(log_frame, height=10,
                                state="disabled", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True)

        self.operator_alert_frame = ttk.Frame(
            self.main_container, padding="10")
        self.operator_alert_frame.pack(fill="x")

        self.alert_var = tk.StringVar(value="Status: Operator obecny")
        self.alert_label = ttk.Label(
            self.operator_alert_frame, textvariable=self.alert_var, font=("Helvetica", 10, "italic"))
        self.alert_label.pack(side="left")

        ttk.Button(self.operator_alert_frame, text="Wyloguj",
                   command=self.logout).pack(side="right")

    def add_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def logout(self):
        self.logged_in = False
        self.production_running = False
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_login()

    def get_cpu_temp(self):
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                return temps['coretemp'][0].current
            elif 'acpitz' in temps:
                return temps['acpitz'][0].current
            return 45.0  
        except:
            return 45.0

    def start_simulation(self):
        if not self.logged_in:
            return

        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        cpu_temp = self.get_cpu_temp()

        self.cpu_usage_label.config(text=f"Użycie CPU: {cpu_usage}%")
        self.cpu_temp_label.config(text=f"Temp. CPU: {cpu_temp:.1f}°C")
        self.mem_usage_label.config(text=f"Użycie RAM: {ram_usage}%")

        target_motor_temp = cpu_temp + \
            (cpu_usage / 4.0) + random.uniform(-2, 2)

        self.motor_temp += (target_motor_temp - self.motor_temp) * 0.1

        if self.motor_temp > 65.0 and not self.fan_active:
            self.fan_active = True
            self.add_log(
                "OSTRZEŻENIE: Wysoka temperatura silnika (>65°C). Włączanie wentylatora.")
            self.fan_status_label.config(
                text="Wentylator Pomocniczy: WŁĄCZONY", foreground="blue")

        elif self.motor_temp > 75.0 and self.production_speed == 100:
            self.production_speed = 50
            self.add_log(
                "ALARM: Krytyczna temperatura (>75°C). Redukcja prędkości do 50%!")
            self.speed_label.config(
                text="Prędkość Linii: 50% (LIMIT)", foreground="red")

        elif self.motor_temp < 60.0 and self.fan_active:
            self.fan_active = False
            self.production_speed = 100
            self.add_log(
                "INFO: Temperatura ustabilizowana. Wyłączanie wentylatora, powrót do 100% prędkości.")
            self.fan_status_label.config(
                text="Wentylator Pomocniczy: WYŁ", foreground="gray")
            self.speed_label.config(
                text="Prędkość Linii: 100%", foreground="black")

        self.motor_temp_label.config(text=f"Temp. Silnika: {
                                     self.motor_temp:.1f}°C")

        if random.random() < 0.05:
            failures = ["Zator na podajniku #2",
                        "Błąd czujnika zbliżeniowego", "Przeciążenie taśmy"]
            fail = random.choice(failures)
            previous_speed = self.production_speed
            self.speed_label.config(
                text="Prędkość Linii: 0%", foreground="black")

            self.add_log(f"AWARIA: {fail}! Wymagana interwencja.")
            messagebox.showwarning("AWARIA", f"Wykryto awarię: {
                                   fail}, Linia zatrzymana")

            self.speed_label.config(
                text=f"Prędkość Linii: {previous_speed}%", foreground="black")

        if self.production_running:
            self.root.after(2000, self.start_simulation)

    def schedule_operator_check(self):
        if not self.logged_in:
            return
        delay = int(20e3)
        self.root.after(delay, self.trigger_presence_check)

    def trigger_presence_check(self):
        if not self.logged_in or self.check_active:
            return

        self.check_active = True
        self.add_log("AUTODIAGNOSTYKA: Proszę potwierdzić obecność operatora.")

        self.check_window = tk.Toplevel(self.root)
        self.check_window.title("Potwierdzenie obecności")
        self.check_window.geometry("300x150")
        self.check_window.attributes("-topmost", True)
        self.check_window.protocol(
            "WM_DELETE_WINDOW", lambda: None)

        ttk.Label(self.check_window, text="CZY JESTEŚ TAM?",
                  font=("Helvetica", 12, "bold")).pack(pady=10)
        self.countdown_var = tk.IntVar(value=30)
        self.timer_label = ttk.Label(
            self.check_window, text="Czas na odpowiedź: 30s", foreground="red")
        self.timer_label.pack()

        ttk.Button(self.check_window, text="POTWIERDZAM OBECNOŚĆ",
                   command=self.confirm_presence).pack(pady=10)

        self.update_countdown()

    def update_countdown(self):
        if not self.check_active:
            return

        count = self.countdown_var.get()
        if count > 0:
            self.countdown_var.set(count - 1)
            self.timer_label.config(text=f"Czas na odpowiedź: {count-1}s")
            self.root.after(1000, self.update_countdown)
        else:
            self.trigger_alarm_and_logout()

    def confirm_presence(self):
        self.check_active = False
        self.check_window.destroy()
        self.add_log("INFO: Obecność potwierdzona.")
        self.schedule_operator_check()

    def trigger_alarm_and_logout(self):
        self.check_active = False
        if hasattr(self, 'check_window'):
            self.check_window.destroy()

        messagebox.showerror(
            "ALARM", "Brak potwierdzenia obecności! Operator wylogowany automatycznie.")
        self.add_log("ALARM: Brak obecności operatora. Wylogowanie awaryjne.")
        self.logout()


if __name__ == "__main__":
    root = tk.Tk()
    app = DispatcherApp(root)
    root.mainloop()

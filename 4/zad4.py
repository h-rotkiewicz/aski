import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

def wczytaj_slownik(sciezka="slownik.txt"):
    if not os.path.exists(sciezka):
        return []

    slowa = []
    with open(sciezka, "r", encoding="utf-8") as plik:
        for linia in plik:
            slowo = linia.strip()
            if slowo:
                slowa.append(slowo)
    return slowa


def cenzuruj_tekst(tekst, slownik):

    if not slownik:
        return tekst

    wynik = tekst
    for slowo in slownik:
        wzorzec = re.compile(rf"\b{re.escape(slowo)}\b", re.IGNORECASE)
        wynik = wzorzec.sub(lambda m: "*" * len(m.group(0)), wynik)

    return wynik

def czy_ascii(tekst):
  
    return all(ord(znak) < 128 for znak in tekst)


def znak_na_bity_ascii(znak):
  
    return format(ord(znak), "08b")


def ascii_na_ramke_rs232(znak):
 
    bity_msb_lsb = znak_na_bity_ascii(znak)
    bity_lsb_msb = bity_msb_lsb[::-1]
    ramka = "0" + bity_lsb_msb + "11"
    return ramka


def tekst_na_strumien_rs232(tekst):
  
    strumien = ""
    for znak in tekst:
        strumien += ascii_na_ramke_rs232(znak)
    return strumien


def ramka_rs232_na_znak(ramka):

    if len(ramka) != 11:
        raise ValueError("Niepoprawna długość ramki.")

    bit_startu = ramka[0]
    bity_danych_lsb_msb = ramka[1:9]
    bity_stopu = ramka[9:11]

    if bit_startu != "0":
        raise ValueError("Niepoprawny bit startu.")
    if bity_stopu != "11":
        raise ValueError("Niepoprawne bity stopu.")

    bity_msb_lsb = bity_danych_lsb_msb[::-1]
    kod_ascii = int(bity_msb_lsb, 2)

    if kod_ascii > 127:
        raise ValueError("Kod spoza zakresu ASCII.")

    return chr(kod_ascii)


def strumien_rs232_na_tekst(strumien):
    if not strumien:
        return ""

    if any(bit not in "01" for bit in strumien):
        raise ValueError("Strumień zawiera znaki inne niż 0 i 1.")

    if len(strumien) % 11 != 0:
        raise ValueError("Długość strumienia nie jest wielokrotnością 11 bitów.")

    wynik = ""
    for i in range(0, len(strumien), 11):
        ramka = strumien[i:i+11]
        znak = ramka_rs232_na_znak(ramka)
        wynik += znak

    return wynik

class AplikacjaRS232:
    def __init__(self, root):
        self.root = root
        self.root.title("Symulator transmisji RS232")
        self.root.geometry("1200x760")
        self.root.minsize(1000, 680)

        self.slownik = wczytaj_slownik("slownik.txt")
        self.medium = ""  

        self.zbuduj_interfejs()
        self.odswiez_status_slownika()

    def zbuduj_interfejs(self):
        styl = ttk.Style()
        styl.configure("TLabel", font=("Arial", 11))
        styl.configure("TButton", font=("Arial", 10))
        styl.configure("TLabelframe.Label", font=("Arial", 12, "bold"))

        glowna_ramka = ttk.Frame(self.root, padding=10)
        glowna_ramka.pack(fill="both", expand=True)

        gorna_ramka = ttk.Frame(glowna_ramka)
        gorna_ramka.pack(fill="both", expand=True)

        self.ramka_nadajnika = ttk.LabelFrame(gorna_ramka, text="Nadajnik", padding=10)
        self.ramka_nadajnika.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.ramka_odbiornika = ttk.LabelFrame(gorna_ramka, text="Odbiornik", padding=10)
        self.ramka_odbiornika.pack(side="left", fill="both", expand=True, padx=(5, 0))

        self.ramka_medium = ttk.LabelFrame(glowna_ramka, text="Nośnik danych / strumień bitów", padding=10)
        self.ramka_medium.pack(fill="both", expand=True, pady=(10, 0))

        self.zbuduj_nadajnik()
        self.zbuduj_odbiornik()
        self.zbuduj_medium()

    def zbuduj_nadajnik(self):
        ttk.Label(self.ramka_nadajnika, text="Tekst wejściowy do nadania (ASCII):").pack(anchor="w")

        self.pole_tekst_nadawany = scrolledtext.ScrolledText(self.ramka_nadajnika, wrap="word", height=10, font=("Consolas", 11))
        self.pole_tekst_nadawany.pack(fill="both", expand=True, pady=(5, 10))
        self.pole_tekst_nadawany.insert("1.0", "To jest test transmisji RS232.")

        ttk.Label(self.ramka_nadajnika, text="Tekst po cenzurze po stronie nadajnika:").pack(anchor="w")

        self.pole_tekst_po_cenzurze = scrolledtext.ScrolledText(self.ramka_nadajnika, wrap="word", height=8, font=("Consolas", 11))
        self.pole_tekst_po_cenzurze.pack(fill="both", expand=True, pady=(5, 10))

        przyciski = ttk.Frame(self.ramka_nadajnika)
        przyciski.pack(fill="x", pady=(5, 0))

        ttk.Button(przyciski, text="1. Cenzuruj tekst", command=self.cenzuruj_po_stronie_nadajnika).pack(side="left", padx=(0, 5))
        ttk.Button(przyciski, text="2. Koduj i wyślij", command=self.koduj_i_wyslij).pack(side="left", padx=5)
        ttk.Button(przyciski, text="Wyczyść nadajnik", command=self.wyczysc_nadajnik).pack(side="left", padx=5)

    def zbuduj_odbiornik(self):
        ttk.Label(self.ramka_odbiornika, text="Tekst odebrany po dekodowaniu:").pack(anchor="w")

        self.pole_tekst_odebrany = scrolledtext.ScrolledText(self.ramka_odbiornika, wrap="word", height=10, font=("Consolas", 11))
        self.pole_tekst_odebrany.pack(fill="both", expand=True, pady=(5, 10))

        ttk.Label(self.ramka_odbiornika, text="Tekst po cenzurze po stronie odbiornika:").pack(anchor="w")

        self.pole_tekst_po_cenzurze_odb = scrolledtext.ScrolledText(self.ramka_odbiornika, wrap="word", height=8, font=("Consolas", 11))
        self.pole_tekst_po_cenzurze_odb.pack(fill="both", expand=True, pady=(5, 10))

        przyciski = ttk.Frame(self.ramka_odbiornika)
        przyciski.pack(fill="x", pady=(5, 0))

        ttk.Button(przyciski, text="3. Odbierz i dekoduj", command=self.odbierz_i_dekoduj).pack(side="left", padx=(0, 5))
        ttk.Button(przyciski, text="Wyczyść odbiornik", command=self.wyczysc_odbiornik).pack(side="left", padx=5)

    def zbuduj_medium(self):
        info_ramka = ttk.Frame(self.ramka_medium)
        info_ramka.pack(fill="x")

        self.etykieta_status_slownika = ttk.Label(info_ramka, text="Słownik: brak")
        self.etykieta_status_slownika.pack(side="left", anchor="w")

        ttk.Button(info_ramka, text="Wczytaj słownik ponownie", command=self.przeladuj_slownik).pack(side="right")

        ttk.Label(self.ramka_medium, text="Strumień bitów RS232 (kolejne ramki po 11 bitów):").pack(anchor="w", pady=(10, 0))

        self.pole_strumien = scrolledtext.ScrolledText(self.ramka_medium, wrap="word", height=12, font=("Consolas", 11))
        self.pole_strumien.pack(fill="both", expand=True, pady=(5, 10))

        dolne_przyciski = ttk.Frame(self.ramka_medium)
        dolne_przyciski.pack(fill="x")

        ttk.Button(dolne_przyciski, text="Wyczyść strumień", command=self.wyczysc_strumien).pack(side="left", padx=(0, 5))
        ttk.Button(dolne_przyciski, text="Zapisz strumień do pliku", command=self.zapisz_strumien_do_pliku).pack(side="left", padx=5)
        ttk.Button(dolne_przyciski, text="Wczytaj strumień z pliku", command=self.wczytaj_strumien_z_pliku).pack(side="left", padx=5)
    # OPERACJE NA SŁOWNIKU
    def odswiez_status_slownika(self):
        if self.slownik:
            self.etykieta_status_slownika.config(
                text=f"Słownik wczytany: {len(self.slownik)} słów (plik: slownik.txt)"
            )
        else:
            self.etykieta_status_slownika.config(
                text="Słownik pusty lub brak pliku slownik.txt"
            )

    def przeladuj_slownik(self):
        self.slownik = wczytaj_slownik("slownik.txt")
        self.odswiez_status_slownika()
        messagebox.showinfo("Słownik", "Ponownie wczytano plik slownik.txt.")
    # NADAJNIK
    def cenzuruj_po_stronie_nadajnika(self):
        tekst = self.pole_tekst_nadawany.get("1.0", "end-1c")

        if not tekst.strip():
            messagebox.showwarning("Brak danych", "Wpisz tekst do nadania.")
            return

        if not czy_ascii(tekst):
            messagebox.showerror(
                "Błąd ASCII",
                "Tekst zawiera znaki spoza klasycznego ASCII.\n"
                "Usuń polskie znaki typu ą, ę, ł, ż itd."
            )
            return

        tekst_po_cenzurze = cenzuruj_tekst(tekst, self.slownik)

        self.pole_tekst_po_cenzurze.delete("1.0", "end")
        self.pole_tekst_po_cenzurze.insert("1.0", tekst_po_cenzurze)

    def koduj_i_wyslij(self):
        tekst = self.pole_tekst_nadawany.get("1.0", "end-1c")

        if not tekst.strip():
            messagebox.showwarning("Brak danych", "Wpisz tekst do nadania.")
            return

        if not czy_ascii(tekst):
            messagebox.showerror(
                "Błąd ASCII",
                "Tekst zawiera znaki spoza klasycznego ASCII.\n"
                "Usuń polskie znaki typu ą, ę, ł, ś, ć, ń, ó, ż, ź."
            )
            return

        # Najpierw cenzura po stronie nadajnika
        tekst_po_cenzurze = cenzuruj_tekst(tekst, self.slownik)

        self.pole_tekst_po_cenzurze.delete("1.0", "end")
        self.pole_tekst_po_cenzurze.insert("1.0", tekst_po_cenzurze)

        # Zamiana na strumień ramek RS232
        self.medium = tekst_na_strumien_rs232(tekst_po_cenzurze)

        self.pole_strumien.delete("1.0", "end")
        self.pole_strumien.insert("1.0", self.medium)

        messagebox.showinfo("Transmisja", "Tekst został zakodowany i przesłany do nośnika danych.")
    # ODBIORNIK
    def odbierz_i_dekoduj(self):
        strumien = self.pole_strumien.get("1.0", "end-1c").strip()

        if not strumien:
            messagebox.showwarning("Brak danych", "Brak strumienia bitów do odebrania.")
            return

        try:
            tekst_odebrany = strumien_rs232_na_tekst(strumien)
            tekst_po_cenzurze = cenzuruj_tekst(tekst_odebrany, self.slownik)

            self.pole_tekst_odebrany.delete("1.0", "end")
            self.pole_tekst_odebrany.insert("1.0", tekst_odebrany)

            self.pole_tekst_po_cenzurze_odb.delete("1.0", "end")
            self.pole_tekst_po_cenzurze_odb.insert("1.0", tekst_po_cenzurze)

            messagebox.showinfo("Odbiór", "Strumień został poprawnie zdekodowany.")
        except ValueError as e:
            messagebox.showerror("Błąd dekodowania", f"Nie udało się zdekodować strumienia:\n{e}")
    # ZAPIS / ODCZYT MEDIUM DO PLIKU
    def zapisz_strumien_do_pliku(self):
        strumien = self.pole_strumien.get("1.0", "end-1c").strip()

        if not strumien:
            messagebox.showwarning("Brak danych", "Nie ma strumienia do zapisania.")
            return

        with open("medium.txt", "w", encoding="utf-8") as plik:
            plik.write(strumien)

        messagebox.showinfo("Plik", "Strumień zapisano do pliku medium.txt.")

    def wczytaj_strumien_z_pliku(self):
        if not os.path.exists("medium.txt"):
            messagebox.showwarning("Brak pliku", "Nie znaleziono pliku medium.txt.")
            return

        with open("medium.txt", "r", encoding="utf-8") as plik:
            dane = plik.read().strip()

        self.medium = dane
        self.pole_strumien.delete("1.0", "end")
        self.pole_strumien.insert("1.0", dane)

        messagebox.showinfo("Plik", "Wczytano strumień z pliku medium.txt.")

    def wyczysc_nadajnik(self):
        self.pole_tekst_nadawany.delete("1.0", "end")
        self.pole_tekst_po_cenzurze.delete("1.0", "end")

    def wyczysc_odbiornik(self):
        self.pole_tekst_odebrany.delete("1.0", "end")
        self.pole_tekst_po_cenzurze_odb.delete("1.0", "end")

    def wyczysc_strumien(self):
        self.pole_strumien.delete("1.0", "end")
        self.medium = ""

if __name__ == "__main__":
    root = tk.Tk()
    app = AplikacjaRS232(root)
    root.mainloop()
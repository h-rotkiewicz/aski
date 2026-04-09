#set page(margin: 2cm)
#set text(font: "Linux Libertine", size: 11pt)

#align(center)[
  #block(inset: 10pt)[
    #text(weight: "bold", size: 18pt)[Sprawozdanie: Zadanie 1] \
    #text(size: 14pt)[Interaktywny Kalkulator z Funkcjami Bitowymi i Zegarem]
  ]
]

== 1. Sformułowanie zadania i założenia
Celem zadania było stworzenie aplikacji z graficznym interfejsem użytkownika umożliwiającej interakcję za pomocą myszy i klawiatury. Przyjęto realizację zaawansowanego kalkulatora wspomagającego operacje bitowe.

*Główne założenia:*
- Interfejs zbudowany w oparciu o bibliotekę `tkinter`.
- Obsługa standardowych operacji matematycznych oraz bitowych takich jak AND, OR, XOR, NOT czy przesunięcia.
- Dynamiczna zmiana motywów graficznych między trybem jasnym a ciemnym.
- Wyświetlanie aktualnego czasu w czasie rzeczywistym.
- Pełna obsługa zdarzeń klawiatury poprzez mapowanie klawiszy na funkcje.

== 2. Opis rozwiązań programowych

=== Wygląd i interakcja
Interfejs został zaprojektowany w układzie siatkowym. Wykorzystano słownik motywów do przechowywania definicji kolorów, co pozwala na natychmiastową aktualizację wyglądu wszystkich komponentów.

```python
self.themes = {
    "dark": {"bg": "#1A1A1A", "display_bg": "#252525", "text": "#FFFFFF", "btn_num": "#333333"},
    "light": {"bg": "#F0F0F0", "display_bg": "#FFFFFF", "text": "#000000", "btn_num": "#FFFFFF"}
}
```

=== Odmierzanie czasu i równoległość
Zastosowano metodę `.after()` pętli głównej `tkinter`. Pozwala to na asynchroniczne aktualizowanie zegara bez blokowania interfejsu użytkownika i zapewnia płynną symulację współbieżności.

```python
def update_clock(self):
    now = time.strftime("%H:%M:%S")
    self.clock_label.config(text=now)
    self.root.after(1000, self.update_clock)
```

=== Logika obliczeń
Obliczenia realizowane są poprzez ewaluację wyrażeń tekstowych. Umożliwia to łatwą obsługę złożonych operacji bitowych. Mapowanie znaków wejściowych pozwala na używanie intuicyjnych symboli dla operatorów przesunięcia.

== 3. Zrzuty ekranu aplikacji

#grid(
  columns: (1fr, 1fr),
  gutter: 10pt,

  [
    #image("Dark.png", width: 100%)
  ],

  [
    #image("Light.png", width: 100%)
  ],
)

== 4. Dyskusja wyników
*Zalety:*
- Intuicyjna obsługa klawiaturą przy użyciu klawiszy Enter oraz Escape.
- Elastyczny system motywów.
- Płynne działanie zegara dzięki nieblokującym wywołaniom.

*Wady:*
- Wykorzystanie funkcji `eval` wymaga ostrożności przy parsowaniu danych wejściowych.
- Brak dźwiękowej sygnalizacji błędów lub naciśnięcia klawiszy.

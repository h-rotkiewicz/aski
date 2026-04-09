#set page(margin: 2cm)
#set text(font: "Linux Libertine", size: 11pt)

#align(center)[
  #block(inset: 10pt)[
    #text(weight: "bold", size: 18pt)[Sprawozdanie: Zadanie 3] 
    #text(size: 14pt)[Symulator Stanowiska Dyspozytorskiego]
  ]
]

== 1. Sformułowanie zadania i założenia
Celem zadania było stworzenie aplikacji symulującej pracę dyspozytora linii produkcyjnej. Program integruje dane diagnostyczne komputera z symulacją procesu przemysłowego oraz nadzoruje aktywność operatora.

*Główne założenia:*
- Pobieranie parametrów pracy komputera poprzez bibliotekę `psutil`.
- Symulacja awarii oraz automatyczne reagowanie na przekroczenia temperatur.
- Mechanizm autodiagnostyki operatora wymagający okresowego potwierdzenia obecności.
- System logowania zabezpieczający dostęp do panelu kontrolnego.

== 2. Opis rozwiązań programowych

=== Diagnostyka systemu i symulacja procesu
Aplikacja odczytuje rzeczywiste dane o zużyciu procesora oraz pamięci RAM. Temperatura silnika linii produkcyjnej jest wyliczana na podstawie temperatury rdzeni procesora, co pozwala na realistyczną symulację obciążenia.

```python
cpu_usage = psutil.cpu_percent()
cpu_temp = self.get_cpu_temp()
# Wyliczanie symulowanej temperatury silnika
self.motor_temp += (target_motor_temp - self.motor_temp) * 0.1
```

=== Odmierzanie czasu i badanie obecności
System autodiagnostyki wykorzystuje dwa niezależne mechanizmy czasowe oparte o metodę `after`. Pierwszy planuje kolejne testy obecności, a drugi zarządza oknem odliczania czasu na odpowiedź.

```python
def update_countdown(self):
    count = self.countdown_var.get()
    if count > 0:
        self.countdown_var.set(count - 1)
        self.root.after(1000, self.update_countdown)
    else:
        self.trigger_alarm_and_logout()
```

=== Równoległość i obsługa zdarzeń
Pętla symulacji działa asynchronicznie względem interfejsu użytkownika, co pozwala na płynną aktualizację wykresów i wskaźników przy jednoczesnym oczekiwaniu na reakcję operatora w osobnym oknie dialogowym.

== 3. Zrzuty ekranu aplikacji

#grid(
  columns: (1fr, 1fr),
  gutter: 10pt,

  [
    #image("Login.png", width: 100%)
  ],

  [
    #image("error.png", width: 100%)
  ],
)


== 4. Dyskusja wyników
*Zalety:*
- Integracja z rzeczywistymi parametrami sprzętowymi komputera.
- Rozbudowany dziennik zdarzeń dokumentujący awarie i akcje systemu.
- Skuteczny mechanizm wylogowania w przypadku braku reakcji.

*Wady:*
- Brak wsparcia dla wielu monitorów przy wyświetlaniu okien alarmowych.
- Zależność od uprawnień systemowych wymaganych do odczytu temperatur.

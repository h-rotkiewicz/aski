#set page(margin: 2cm)
#set text(font: "Linux Libertine", size: 11pt)

#align(center)[
  #block(inset: 10pt)[
    #text(weight: "bold", size: 18pt)[Sprawozdanie: Zadanie 2] 
    #text(size: 14pt)[Tester Sprawności Psychomotorycznej]
  ]
]

== 1. Sformułowanie zadania i założenia
Celem zadania było zaprojektowanie aplikacji do pomiaru czasu reakcji na bodźce optyczne oraz akustyczne. Program służy jako narzędzie do wstępnej oceny zdolności psychomotorycznych.

*Główne założenia:*
- Realizacja testów reakcji prostej oraz wyboru.
- Zastosowanie fazy szkoleniowej przed właściwym testem.
- Precyzyjny pomiar czasu z dokładnością do milisekund.
- Prezentacja wyników w formie analitycznej po zakończeniu serii.

== 2. Opis rozwiązań programowych

=== Precyzyjny pomiar czasu
Do odmierzania interwałów wykorzystano funkcję `time.perf_counter`, która zapewnia najwyższą dostępną rozdzielczość zegara w systemie. Różnica między momentem wystąpienia bodźca a reakcją użytkownika jest przeliczana na milisekund.

```python
self.start_time = time.perf_counter()
# ... po wystąpieniu zdarzenia
reaction_time = (time.perf_counter() - self.start_time) * 1000
```

=== Sygnalizacja dźwiękowa
Odtwarzanie dźwięku zrealizowano poprzez wywołanie systemowego procesu `paplay` lub wysłanie sygnału alarmowego do terminala. Dzięki temu aplikacja nie wymaga zewnętrznych bibliotek multimedialnych.

```python
subprocess.Popen(["paplay", "/usr/share/sounds/ocean/stereo/bell.oga"])
```

=== Zarządzanie testami i równoległość
Logika testów opiera się na asynchronicznym planowaniu zdarzeń. Funkcja `root.after` pozwala na wprowadzenie losowego opóźnienia przed bodźcem bez zawieszania interfejsu graficznego.

== 3. Zrzuty ekranu aplikacji

#grid(
  columns: (1fr, 1fr),
  gutter: 10pt,
  [ #rect(width: 100%, height: 150pt, stroke: 1pt + gray)[*Miejsce na screenshot: Instrukcja i wybór testu*] ],
  [ #rect(width: 100%, height: 150pt, stroke: 1pt + gray)[*Miejsce na screenshot: Wyniki końcowe*] ]
)

== 4. Dyskusja wyników
*Zalety:*
- Bardzo wysoka precyzja pomiaru dzięki licznikom procesora.
- Jasny podział na trening i test właściwy.
- Obsługa błędnych reakcji oraz prób przedwczesnych.

*Wady:*
- Metoda odtwarzania dźwięku zależy od zainstalowanych narzędzi w systemie operacyjnym.
- Minimalistyczna oprawa graficzna skupiona wyłącznie na funkcjonalności.

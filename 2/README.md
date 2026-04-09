# Psychomotor Reaction Timer

A simple desktop application built with Python and Tkinter to measure psychomotor reaction time using visual and auditory stimuli.

## Features
- **Test Sequence**: Simple Visual, Choice Visual, and Simple Auditory tests.
- **Phases**: Each test includes an instruction screen, a practice phase (not recorded), and a real test phase.
- **Stimuli**:
  - Simple Visual: Screen turns RED.
  - Choice Visual: RED or GREEN square appears (Press 'R' or 'G').
  - Simple Auditory: System sound plays.
- **Results**: Displays average reaction time, correct responses, errors, and a text-based graphical representation.
- **Controls**:
  - SPACE: General reaction key.
  - R/G: Choice keys for visual test.
  - ESC: Return to main menu during a test.

## Requirements
- Python 3.x
- Tkinter (usually included with Python)
- `aplay` or `paplay` (for auditory stimuli on Linux)

## How to Run
```bash
python3 main.py
```

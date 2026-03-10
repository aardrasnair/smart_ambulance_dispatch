# 🚑 Smart Ambulance Dispatch System

A real-time dispatch and triage system designed to optimize patient outcomes by finding the fastest path to the most suitable hospital.

## 🚀 Getting Started

To run the interactive dispatch system:
```bash
python3 run_app.py
```

To run the automated CLI demonstration:
```bash
python3 main.py
```

## ✨ Features

- **🏆 Real-time Hospital Ranking**: Automatically ranks hospitals based on travel time and processing delay.
- **🚥 Traffic-Aware Routing**: Uses Dijkstra's algorithm with live traffic density and signal phases.
- **🩺 Intelligent Triage**: Uses the Injury Severity Score (ISS) to match patients with the right specialists.
- **🔄 Conflict Resolution**: Automatically redirects patients if the primary hospital is full or lacks required specialists.
- **🏥 System Monitoring**: Real-time view of hospital bed capacity and doctor availability.

## 📁 Project Structure

- `run_app.py`: The main interactive user interface.
- `main.py`: CLI-based demonstration of dispatch scenarios.
- `src/`: Core logic (routing, hospital management, dispatch, UI).

## 🛠 Requirements

- Python 3.x
- `requirements.txt` (none currently needed for core features)

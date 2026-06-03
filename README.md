# Walkthrough: AppForge Compiler OS

The AppForge Compiler OS is a fully engineered, multi-stage compiler that converts open-ended natural language instructions into strict, validated, and immediately executable application schemas. 

It integrates a cross-layer semantic validation suite, a targeted self-repair loop, and an interactive runtime simulation environment (mock database & router sandbox) that enables live application preview and data entry testing.


## Operating Instructions

### Running the Dashboard Locally
1. Start the Flask server:
   ```powershell
   python main.py
   ```
2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### Running the Test Suite
To run the automated tests:
```powershell
python -m unittest tests.py
```
### Demo Frontend
<img width="1917" height="979" alt="Screenshot 2026-06-03 194921" src="https://github.com/user-attachments/assets/fc086bd6-6f7d-45f8-9a06-f7289ced95de" />

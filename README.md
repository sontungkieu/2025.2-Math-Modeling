# Pedestrian Flow Model

This project implements and analyzes a microscopic model of pedestrian flow based on the principles described in the paper "Basics of modelling the pedestrian flow". The model simulates pedestrians as hard bodies with and without remote (anticipatory) action, and investigates the relationship between pedestrian density and velocity.

## Features

- **Microscopic simulation** of pedestrian movement in a 1D corridor.
- **Configurable parameters**: corridor length, relaxation time, interaction range, desired speed, etc.
- **Support for remote action**: pedestrians can anticipate and react to others ahead.
- **Data output**: simulation results are saved as CSV files.
- **Visualization utilities**: generate spatio-temporal plots and velocity-density diagrams.

## Project Structure

- `main.py` — Runs experiments, sweeps parameters, and saves results.
- `model.py` — Core simulation logic and model implementation.
- `utils.py` — Plotting and analysis utilities.
- `plot_figures.py` — Generates modern and paper-style figures from experiment CSV outputs.
- `interactive_demo.html` — Browser-based interactive demo for the 1D periodic corridor model.
- `docs/assets/` — README images and other documentation assets.
- `output/` — Directory for generated CSV and PNG files.
- `slides/math_modelling/` — Beamer slide deck extracted from `Math_Modelling.zip` with updated figures.

## Model Convention

- Pedestrians move in the increasing `x` direction on a periodic 1D corridor.
- The pedestrian in front of pedestrian `i` is `(i + 1) % N`.
- Front distance is `(x[(i + 1) % N] - x[i]) % L`.
- `simulate(..., seed=...)` can be used for deterministic runs; leaving `seed=None` keeps non-deterministic sampling.

## Getting Started

### Prerequisites

- `uv`
- Python 3.10, pinned in `.python-version`
- Dependencies are managed in `pyproject.toml` and locked in `uv.lock`.
- The locked dependencies are verified for Linux and Windows with Python 3.10.

### Install uv

Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Open a new terminal if `uv` is not found after installation.

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/ankhanhtran02/Pedestrian-Flow.git
    cd Pedestrian-Flow
    ```

2. Install Python 3.10 and the locked dependencies:
    ```bash
    uv python install 3.10
    uv sync --locked
    ```

### Running Simulations

To run the main experiment and generate data:
```bash
uv run python main.py
```

Run a specific experiment:
```bash
uv run python main.py --experiment exp1
uv run python main.py --experiment exp2
uv run python main.py --experiment exp3
```

`exp3` writes the stop-and-go comparison inputs `output/exp3_rho_1_16.csv` and `output/exp3_rho_1_21.csv`; `output/exp3.csv` remains the first case for backward-compatible plotting commands.

Run all experiments:
```bash
uv run python main.py --experiment all
```

### Generating Figures

After CSV outputs exist in `output/`, generate modern presentation figures and compact paper-style figures:
```bash
uv run python plot_figures.py
```

Generate only selected experiments or styles:
```bash
uv run python plot_figures.py --experiments exp1 exp3 --styles paper
```

### LaTeX Slides

The Beamer slide deck is in `slides/math_modelling/`.

Regenerate the slide figures:
```bash
uv run python slides/math_modelling/generate_slide_figures.py
```

Submit the heavier sensitivity-figure run to Kaggle GPU:
```bash
uv run --with kaggle python scripts/submit_kaggle_slide_figures.py
```

Check the submitted job status:
```bash
uv run --with kaggle python scripts/submit_kaggle_slide_figures.py --status-ref <owner>/<slug>
```

Download the finished Kaggle output:
```bash
uv run --with kaggle python scripts/submit_kaggle_slide_figures.py --download-ref <owner>/<slug>
```

The Kaggle job recomputes the heavier parameter-sweep figure only and writes `generated_slide_figures.zip` with refreshed `body_length.png` and its CSV data. By default the submit helper uses GPU, 4 workers, 3 seed repeats, and a longer simulation horizon than the local slide default. Use `--owner <kaggle_username>` to select a specific Kaggle account.

Build the slide PDF:
```bash
cd slides/math_modelling
latexmk -pdf main.tex
latexmk -c main.tex
```

### Interactive Demo

![Interactive pedestrian-flow demo](docs/assets/interactive_demo.png)

Open `interactive_demo.html` directly in a browser, or serve the repository with a local static server:

```bash
uv run python -m http.server 8765 --bind 0.0.0.0
```

Then open:

```text
http://127.0.0.1:8765/interactive_demo.html
```

In VS Code on WSL, run `Simple Browser: Show` from the command palette and paste the same URL. If port `8765` is already used, replace it with another free port such as `8766`.
Use the VI/EN toggle in the demo header to switch the interface language. The desired-speed and relaxation-time sliders use `0.01` increments, with defaults `v0 = 1.26 m/s` and `tau = 0.61 s`. Reset pauses the demo and returns the current parameter set to the deterministic `t = 0` state; Back restores the previous rendered frame; Step advances one rendered frame using the current steps/frame speed. The red dashed segment shows the highlighted pedestrian's front gap as an absolute distance `s` and as a ratio `s/d_i` to the required hard-body length. In Hard-body mode, orange rings in the space-time plot mark pedestrians whose step was stopped and rolled back by the hard-body constraint.

### Running Tests

```bash
uv run pytest
```

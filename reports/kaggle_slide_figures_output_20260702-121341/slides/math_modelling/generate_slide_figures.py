from __future__ import annotations

import argparse
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SLIDE_DIR = Path(__file__).resolve().parent
DATA_DIR = SLIDE_DIR / "generated_data"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from plot_figures import (  # noqa: E402
    BLUE,
    ORANGE,
    PURPLE,
    _add_modern_header,
    _configure_velocity_axes,
    _new_figure,
    _set_rc,
    _style_axes,
    _style_legend,
)

A = 0.36
B = 0.56
DT = 0.001
L_DEFAULT = 17.3
TAU = 0.61
V0_MEAN = 1.24
E = 0.07
F = 2.0
T_RELAX = 2_000
T_MEASURE = 2_000
DENSITIES = np.linspace(0.35, 2.35, 6)
REPEATS = 1
WORKERS = 1


def copy_existing_outputs() -> None:
    mapping = {
        ROOT / "output" / "exp1_modern.png": SLIDE_DIR / "no_remote_action.png",
        ROOT / "output" / "exp2_modern.png": SLIDE_DIR / "remote_action.png",
        ROOT / "output" / "exp3_modern.png": SLIDE_DIR / "stop_and_go.png",
    }
    for source, target in mapping.items():
        if not source.exists():
            raise FileNotFoundError(f"Missing source figure: {source}")
        shutil.copy2(source, target)

    source_fundamental = SLIDE_DIR / "fundamental_diagram.png.jpg"
    if source_fundamental.exists():
        Image.open(source_fundamental).save(SLIDE_DIR / "fundamental_diagram.png")


def enforce_no_overlap_fast(
    x_old: np.ndarray,
    x_new: np.ndarray,
    v_new: np.ndarray,
    corridor_length: float,
) -> tuple[np.ndarray, np.ndarray]:
    n_pedestrians = len(x_new)
    gaps = (np.roll(x_new, -1) - x_new) % corridor_length
    needed = A + B * v_new
    if np.all(gaps + 1e-10 >= needed):
        return x_new, v_new

    pending = list(range(n_pedestrians - 1, -1, -1))
    guard = 0

    while pending and guard < n_pedestrians * n_pedestrians * 3:
        guard += 1
        i = pending.pop(0)
        front = (i + 1) % n_pedestrians
        follower = (i + n_pedestrians - 1) % n_pedestrians
        gap = (x_new[front] - x_new[i]) % corridor_length
        needed = A + B * v_new[i]
        already_stopped = v_new[i] == 0 and abs(x_new[i] - x_old[i]) < 1e-10
        if gap + 1e-10 >= needed or already_stopped:
            continue

        v_new[i] = 0
        x_new[i] = x_old[i]
        pending.append(follower)

    return x_new, v_new


def simulate_fast(
    *,
    n_pedestrians: int,
    corridor_length: float,
    v0_std: float,
    seed: int,
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    v0 = rng.normal(loc=V0_MEAN, scale=v0_std, size=n_pedestrians)
    v0 = np.clip(v0, 0.1, None)
    v = np.zeros(n_pedestrians)
    x = np.arange(n_pedestrians, dtype=float) * A
    velocities: list[float] = []

    for step in range(T_RELAX + T_MEASURE):
        front_x = np.roll(x, -1)
        gaps = (front_x - x) % corridor_length
        needed = A + B * v
        forces = np.where(gaps > needed, (v0 - v) / TAU, -v / DT)
        next_v = np.clip(v + DT * forces, 0, v0)
        next_x = (x + next_v * DT) % corridor_length
        next_x, next_v = enforce_no_overlap_fast(x, next_x, next_v, corridor_length)
        x = next_x
        v = next_v
        if step >= T_RELAX:
            velocities.append(float(np.mean(v)))

    return n_pedestrians / corridor_length, float(np.mean(velocities))


def simulate_case(args: tuple[int, float, float, float, int, int]) -> dict[str, float] | None:
    density_index, target_density, corridor_length, v0_std, seed_offset, repeat_index = args
    n_pedestrians = max(2, int(np.floor(float(target_density) * corridor_length)))
    if A * n_pedestrians >= corridor_length:
        return None
    rho, mean_velocity = simulate_fast(
        n_pedestrians=n_pedestrians,
        corridor_length=corridor_length,
        v0_std=v0_std,
        seed=2026 + seed_offset + density_index * max(1, REPEATS) + repeat_index,
    )
    return {
        "rho": rho,
        "mean_velocity": mean_velocity,
        "N": float(n_pedestrians),
        "L": corridor_length,
        "v0_std": v0_std,
        "repeat": float(repeat_index),
    }


def run_curve(
    *,
    densities: Iterable[float],
    corridor_length: float,
    v0_std: float,
    seed_offset: int,
) -> list[dict[str, float]]:
    tasks = [
        (density_index, float(target_density), corridor_length, v0_std, seed_offset, repeat_index)
        for density_index, target_density in enumerate(densities)
        for repeat_index in range(REPEATS)
    ]

    if WORKERS > 1:
        with ProcessPoolExecutor(max_workers=WORKERS) as executor:
            raw_rows = list(executor.map(simulate_case, tasks))
    else:
        raw_rows = [simulate_case(task) for task in tasks]

    rows = [row for row in raw_rows if row is not None]
    if not rows:
        return []

    df = pd.DataFrame(rows)
    grouped = (
        df.groupby(["rho", "N", "L", "v0_std"], as_index=False)["mean_velocity"]
        .mean()
        .sort_values("rho")
    )
    return [
        {
            "rho": float(row.rho),
            "mean_velocity": float(row.mean_velocity),
            "N": float(row.N),
            "L": float(row.L),
            "v0_std": float(row.v0_std),
        }
        for row in grouped.itertuples(index=False)
    ]


def make_velocity_dispersion_data(force: bool) -> Path:
    path = DATA_DIR / "velocity_dispersion.csv"
    if path.exists() and not force:
        return path

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, float]] = []
    for series_index, sigma in enumerate([0.01, 0.05, 0.10]):
        rows.extend(
            run_curve(
                densities=DENSITIES,
                corridor_length=L_DEFAULT,
                v0_std=sigma,
                seed_offset=1000 * series_index,
            )
        )
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def make_system_size_data(force: bool) -> Path:
    path = DATA_DIR / "system_size.csv"
    if path.exists() and not force:
        return path

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, float]] = []
    for series_index, corridor_length in enumerate([17.3, 20.0, 50.0]):
        rows.extend(
            run_curve(
                densities=DENSITIES,
                corridor_length=corridor_length,
                v0_std=0.05,
                seed_offset=10_000 + 1000 * series_index,
            )
        )
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def plot_grouped_curves(
    csv_path: Path,
    *,
    group_column: str,
    output_path: Path,
    title: str,
    subtitle: str,
    label_prefix: str,
    label_format: str,
) -> None:
    _set_rc("modern")
    df = pd.read_csv(csv_path).sort_values([group_column, "rho"])
    fig, ax = _new_figure("modern")
    colors = [BLUE, ORANGE, PURPLE, "#0F766E"]
    markers = ["o", "s", "D", "^"]

    for index, value in enumerate(sorted(df[group_column].unique())):
        sub = df[df[group_column] == value]
        color = colors[index % len(colors)]
        marker = markers[index % len(markers)]
        label = f"{label_prefix} = {format(float(value), label_format)}"
        ax.plot(sub["rho"], sub["mean_velocity"], color=color, linewidth=1.85, alpha=0.88, zorder=2)
        ax.scatter(
            sub["rho"],
            sub["mean_velocity"],
            s=42,
            marker=marker,
            color=color,
            edgecolor="white",
            linewidth=1.05,
            label=label,
            zorder=3,
        )

    _add_modern_header(fig, title, subtitle)
    _configure_velocity_axes(ax, xmax=3.0, ymax=1.35)
    _style_axes(ax, "modern")
    legend = ax.legend(
        loc="upper right",
        frameon=True,
        fancybox=True,
        framealpha=0.96,
        borderpad=0.65,
        handlelength=1.8,
        labelspacing=0.65,
        borderaxespad=0.55,
    )
    _style_legend(legend, "modern")
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.135, top=0.86)
    fig.savefig(output_path, bbox_inches="tight", pad_inches=0.08, dpi=320)
    plt.close(fig)


def generate(force: bool, copy_existing: bool = True) -> None:
    if copy_existing:
        copy_existing_outputs()
    velocity_csv = make_velocity_dispersion_data(force)
    system_csv = make_system_size_data(force)
    plot_grouped_curves(
        velocity_csv,
        group_column="v0_std",
        output_path=SLIDE_DIR / "velocity.png",
        title="Velocity-density response",
        subtitle="Sensitivity to intended-speed dispersion",
        label_prefix=r"$\sigma$",
        label_format=".2f",
    )
    plot_grouped_curves(
        system_csv,
        group_column="L",
        output_path=SLIDE_DIR / "system_size.png",
        title="Velocity-density response",
        subtitle="Robustness across periodic corridor lengths",
        label_prefix="L",
        label_format=".1f",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate figures used by the Beamer slide deck.")
    parser.add_argument("--force", action="store_true", help="Regenerate cached sensitivity CSV data.")
    parser.add_argument("--t-relax", type=int, default=T_RELAX, help="Relaxation steps for generated sensitivity curves.")
    parser.add_argument("--t-measure", type=int, default=T_MEASURE, help="Measurement steps for generated sensitivity curves.")
    parser.add_argument("--density-count", type=int, default=len(DENSITIES), help="Number of target density points.")
    parser.add_argument("--density-min", type=float, default=float(DENSITIES[0]), help="Minimum target density.")
    parser.add_argument("--density-max", type=float, default=float(DENSITIES[-1]), help="Maximum target density.")
    parser.add_argument("--repeats", type=int, default=REPEATS, help="Seed repeats averaged for each condition.")
    parser.add_argument("--workers", type=int, default=WORKERS, help="Parallel worker processes for simulations.")
    parser.add_argument(
        "--skip-existing-output-copy",
        action="store_true",
        help="Only regenerate sensitivity figures; do not copy exp1/exp2/exp3 figures from output/.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    T_RELAX = args.t_relax
    T_MEASURE = args.t_measure
    DENSITIES = np.linspace(args.density_min, args.density_max, args.density_count)
    REPEATS = max(1, args.repeats)
    WORKERS = max(1, args.workers)
    generate(args.force, copy_existing=not args.skip_existing_output_copy)

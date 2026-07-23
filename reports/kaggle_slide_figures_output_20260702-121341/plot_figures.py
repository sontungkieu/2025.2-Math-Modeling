from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MultipleLocator


BLUE = "#2563EB"
ORANGE = "#EA580C"
PURPLE = "#7C3AED"
SLATE = "#334155"
GRID = "#CBD5E1"
AXIS = "#94A3B8"
BG = "#FBFBFD"

EXP1_SERIES = {
    0.00: ("b = 0", BLUE, "o"),
    0.56: ("b = 0.56", ORANGE, "s"),
    1.06: ("b = 1.06", PURPLE, "D"),
}

EXP2_SERIES = {
    (0, 0.56): ("No remote action, b = 0.56", BLUE, "o"),
    (1, 0.00): ("Remote action, b = 0", ORANGE, "s"),
    (1, 0.56): ("Remote action, b = 0.56", PURPLE, "D"),
}


def _set_rc(style: str) -> None:
    if style == "modern":
        plt.rcParams.update(
            {
                "font.family": "DejaVu Sans",
                "font.size": 9.5,
                "axes.labelsize": 10.5,
                "legend.fontsize": 8.8,
                "xtick.labelsize": 9.2,
                "ytick.labelsize": 9.2,
                "axes.linewidth": 0.8,
                "savefig.dpi": 320,
            }
        )
    else:
        plt.rcParams.update(
            {
                "font.family": "DejaVu Sans",
                "font.size": 8.4,
                "axes.labelsize": 9.2,
                "legend.fontsize": 7.5,
                "xtick.labelsize": 8.0,
                "ytick.labelsize": 8.0,
                "axes.linewidth": 0.7,
                "savefig.dpi": 420,
            }
        )


def _new_figure(style: str) -> tuple[plt.Figure, plt.Axes]:
    if style == "modern":
        fig, ax = plt.subplots(figsize=(7.2, 4.45), dpi=180)
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        return fig, ax

    fig, ax = plt.subplots(figsize=(5.55, 3.45), dpi=220)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    return fig, ax


def _style_axes(ax: plt.Axes, style: str, grid_alpha: float = 0.55) -> None:
    grid_width = 0.65 if style == "modern" else 0.45
    ax.grid(True, which="major", color=GRID, linewidth=grid_width, alpha=grid_alpha)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(AXIS)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(colors=SLATE, length=3.0 if style == "modern" else 2.5, width=0.7)


def _style_legend(legend: plt.Legend, style: str) -> None:
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_edgecolor("#E2E8F0")
    legend.get_frame().set_linewidth(0.7 if style == "modern" else 0.65)


def _add_modern_header(fig: plt.Figure, title: str, subtitle: str) -> None:
    fig.text(0.105, 0.965, title, fontsize=13.2, fontweight="semibold", color="#101828")
    fig.text(0.105, 0.925, subtitle, fontsize=9.2, color="#667085")


def _save(fig: plt.Figure, output_prefix: Path, style: str) -> list[Path]:
    paths = [
        output_prefix.with_name(f"{output_prefix.name}_{style}.png"),
        output_prefix.with_name(f"{output_prefix.name}_{style}.pdf"),
    ]
    pad_inches = 0.08 if style == "modern" else 0.025
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, bbox_inches="tight", pad_inches=pad_inches)
    plt.close(fig)
    return paths


def _configure_velocity_axes(ax: plt.Axes, xmax: float = 3.0, ymax: float = 1.35) -> None:
    ax.set_xlabel(r"Density $\rho$ [1/m]", color="#101828")
    ax.set_ylabel(r"Mean velocity $\bar{v}$ [m/s]", color="#101828")
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.xaxis.set_major_locator(MultipleLocator(0.5))
    ax.yaxis.set_major_locator(MultipleLocator(0.2))


def plot_exp1(csv_path: Path, output_prefix: Path, style: str) -> list[Path]:
    _set_rc(style)
    df = pd.read_csv(csv_path)
    df["b"] = df["b"].astype(float)
    df = df.sort_values(["b", "rho"])

    fig, ax = _new_figure(style)
    for b in sorted(df["b"].unique()):
        sub = df[df["b"] == b]
        label, color, marker = EXP1_SERIES.get(round(float(b), 2), (f"b = {b:g}", BLUE, "o"))
        line_width = 1.85 if style == "modern" else 1.45
        marker_size = 42 if style == "modern" else 24
        edge_width = 1.05 if style == "modern" else 0.75
        ax.plot(sub["rho"], sub["mean_velocity"], color=color, linewidth=line_width, alpha=0.88, zorder=2)
        ax.scatter(
            sub["rho"],
            sub["mean_velocity"],
            s=marker_size,
            marker=marker,
            color=color,
            edgecolor="white",
            linewidth=edge_width,
            label=label.replace(" = ", "=") if style == "paper" else label,
            zorder=3,
        )

    if style == "modern":
        _add_modern_header(
            fig,
            "Velocity-density response",
            "Hard-body model without remote action; sensitivity to body-length coefficient b",
        )

    _configure_velocity_axes(ax, xmax=3.0, ymax=1.35 if style == "modern" else 1.32)
    _style_axes(ax, style)
    legend = ax.legend(
        loc="upper right",
        frameon=True,
        fancybox=style == "modern",
        framealpha=0.96,
        borderpad=0.65 if style == "modern" else 0.45,
        handlelength=1.8 if style == "modern" else 1.55,
        labelspacing=0.65 if style == "modern" else 0.45,
        borderaxespad=0.55,
    )
    _style_legend(legend, style)

    if style == "modern":
        fig.subplots_adjust(left=0.105, right=0.985, bottom=0.135, top=0.86)
    else:
        fig.tight_layout(pad=0.45)
    return _save(fig, output_prefix, style)


def plot_exp2(csv_path: Path, output_prefix: Path, style: str) -> list[Path]:
    _set_rc(style)
    df = pd.read_csv(csv_path)
    df["remote_action"] = df["remote_action"].astype(int)
    df["b"] = df["b"].astype(float)
    df = df.sort_values(["remote_action", "b", "rho"])

    fig, ax = _new_figure(style)
    for (remote, b), (label, color, marker) in EXP2_SERIES.items():
        sub = df[(df["remote_action"] == remote) & (df["b"].round(2) == round(b, 2))]
        if sub.empty:
            continue
        line_width = 1.85 if style == "modern" else 1.45
        marker_size = 42 if style == "modern" else 24
        edge_width = 1.05 if style == "modern" else 0.75
        ax.plot(sub["rho"], sub["mean_velocity"], color=color, linewidth=line_width, alpha=0.88, zorder=2)
        ax.scatter(
            sub["rho"],
            sub["mean_velocity"],
            s=marker_size,
            marker=marker,
            color=color,
            edgecolor="white",
            linewidth=edge_width,
            label=label.replace(" action", "").replace(" = ", "=") if style == "paper" else label,
            zorder=3,
        )

    if style == "modern":
        _add_modern_header(
            fig,
            "Velocity-density response",
            "1D periodic pedestrian flow after front-neighbor collision fix",
        )

    _configure_velocity_axes(ax, xmax=2.9 if style == "modern" else 2.85, ymax=1.35 if style == "modern" else 1.32)
    _style_axes(ax, style)
    legend = ax.legend(
        loc="upper right",
        frameon=True,
        fancybox=style == "modern",
        framealpha=0.96,
        borderpad=0.65 if style == "modern" else 0.45,
        handlelength=1.8 if style == "modern" else 1.55,
        labelspacing=0.65 if style == "modern" else 0.45,
        borderaxespad=0.55,
    )
    _style_legend(legend, style)

    if style == "modern":
        fig.subplots_adjust(left=0.105, right=0.985, bottom=0.135, top=0.86)
    else:
        fig.tight_layout(pad=0.45)
    return _save(fig, output_prefix, style)


def plot_exp3(csv_path: Path, output_prefix: Path, style: str, corridor_length: float, highlight_index: int) -> list[Path]:
    _set_rc(style)
    data = np.loadtxt(csv_path, delimiter=",")
    if data.ndim == 1:
        data = data.reshape(1, -1)
    frame_count, pedestrian_count = data.shape
    frame_index = np.arange(frame_count)
    highlight_index = min(max(highlight_index, 0), pedestrian_count - 1)

    fig, ax = _new_figure(style)
    for pedestrian_index in range(pedestrian_count):
        if pedestrian_index == highlight_index:
            continue
        ax.scatter(
            data[:, pedestrian_index],
            frame_index,
            s=24 if style == "modern" else 13,
            marker="o",
            facecolors="none",
            edgecolors=BLUE,
            linewidths=0.95 if style == "modern" else 0.55,
            alpha=0.68 if style == "modern" else 0.65,
            zorder=2,
        )

    ax.scatter(
        data[:, highlight_index],
        frame_index,
        s=30 if style == "modern" else 18,
        marker="o",
        color=ORANGE,
        edgecolors="white",
        linewidths=0.85 if style == "modern" else 0.55,
        label="tracked pedestrian",
        zorder=3,
    )

    if style == "modern":
        _add_modern_header(
            fig,
            "Spatio-temporal pedestrian positions",
            f"Periodic corridor snapshot; N={pedestrian_count}, frames={frame_count}",
        )

    ax.set_xlabel("Position x [m]", color="#101828")
    ax.set_ylabel("Frame index", color="#101828")
    ax.set_xlim(0, corridor_length)
    ax.set_ylim(-0.5, frame_count - 0.5)
    ax.invert_yaxis()
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.yaxis.set_major_locator(MultipleLocator(5))
    _style_axes(ax, style, grid_alpha=0.48 if style == "modern" else 0.5)
    legend = ax.legend(
        loc="upper right",
        frameon=True,
        fancybox=style == "modern",
        framealpha=0.96,
        borderpad=0.65 if style == "modern" else 0.45,
        handlelength=1.4 if style == "modern" else 1.2,
        labelspacing=0.45,
        borderaxespad=0.55,
    )
    _style_legend(legend, style)

    if style == "modern":
        fig.subplots_adjust(left=0.105, right=0.985, bottom=0.135, top=0.86)
    else:
        fig.tight_layout(pad=0.45)
    return _save(fig, output_prefix, style)


def generate_figures(
    output_dir: Path,
    experiments: Iterable[str],
    styles: Iterable[str],
    corridor_length: float,
    highlight_index: int,
) -> list[Path]:
    generated: list[Path] = []
    experiments = list(experiments)
    styles = list(styles)

    for style in styles:
        if "exp1" in experiments:
            generated.extend(plot_exp1(output_dir / "exp1.csv", output_dir / "exp1", style))
        if "exp2" in experiments:
            generated.extend(plot_exp2(output_dir / "exp2.csv", output_dir / "exp2", style))
        if "exp3" in experiments:
            generated.extend(plot_exp3(output_dir / "exp3.csv", output_dir / "exp3", style, corridor_length, highlight_index))

    return generated


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate modern paper-style figures from experiment CSV outputs.")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Directory containing exp1.csv, exp2.csv, exp3.csv.")
    parser.add_argument(
        "--experiments",
        nargs="+",
        choices=["exp1", "exp2", "exp3", "all"],
        default=["all"],
        help="Experiments to plot.",
    )
    parser.add_argument(
        "--styles",
        nargs="+",
        choices=["modern", "paper", "all"],
        default=["all"],
        help="Figure styles to generate.",
    )
    parser.add_argument("--corridor-length", type=float, default=17.3, help="Corridor length used for exp3 position plots.")
    parser.add_argument("--highlight-index", type=int, default=1, help="Pedestrian index highlighted in exp3.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    experiments = ["exp1", "exp2", "exp3"] if "all" in args.experiments else args.experiments
    styles = ["modern", "paper"] if "all" in args.styles else args.styles
    generated = generate_figures(args.output_dir, experiments, styles, args.corridor_length, args.highlight_index)
    for path in generated:
        print(f"saved={path}")


if __name__ == "__main__":
    main()

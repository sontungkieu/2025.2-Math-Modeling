from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

from model import simulate


BASE_CONFIG: dict[str, float] = {
    "L": 17.3,
    "dt": 0.001,
    "T_relax": 3 * 10**5,
    "T_measure": 3 * 10**5,
    "tau": 0.61,
    "a": 0.36,
    "v0_mean": 1.24,
    "v0_std": 0.05,
    "e": 0.07,
    "f": 2.0,
}


def save_config(output_dir: Path, experiment_name: str, config: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    config_path = output_dir / f"{experiment_name}_config.json"
    with config_path.open("w") as f:
        json.dump(config, f, indent=4)
    print(f"Config saved to {config_path}")


def run_velocity_density_experiment(
    experiment_name: str,
    output_dir: Path,
    rho_targets: np.ndarray,
    params: list[dict[str, Any]],
    include_remote_action: bool,
    seed: int | None,
) -> Path:
    config = dict(BASE_CONFIG)
    if not include_remote_action:
        config["use_remote"] = False
    save_config(output_dir, experiment_name, config)

    output_path = output_dir / f"{experiment_name}.csv"
    fieldnames = ["rho", "b", "mean_velocity"]
    if include_remote_action:
        fieldnames.append("remote_action")

    with output_path.open("w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for target_rho in rho_targets:
            n_pedestrians = int(np.floor(float(target_rho) * float(config["L"])))
            for param_index, param in enumerate(params):
                remote_action = bool(param.get("remote_action", False))
                b = float(param["b"])
                run_seed = None if seed is None else seed + len(params) * n_pedestrians + param_index
                rho, mean_velocity = simulate(
                    N=n_pedestrians,
                    L=float(config["L"]),
                    dt=float(config["dt"]),
                    T_relax=int(config["T_relax"]),
                    T_measure=int(config["T_measure"]),
                    a=float(config["a"]),
                    b=b,
                    tau=float(config["tau"]),
                    v0_mean=float(config["v0_mean"]),
                    v0_std=float(config["v0_std"]),
                    use_remote=remote_action,
                    e=float(config["e"]),
                    f=float(config["f"]),
                    seed=run_seed,
                )
                print(
                    f"rho: {rho:.2f}, b: {b:.2f}, "
                    f"mean_velocity: {mean_velocity:.4f}, remote_action: {remote_action}"
                )
                row: dict[str, float | int] = {
                    "rho": rho,
                    "b": b,
                    "mean_velocity": mean_velocity,
                }
                if include_remote_action:
                    row["remote_action"] = 1 if remote_action else 0
                writer.writerow(row)
                csvfile.flush()

    return output_path


def run_exp1(output_dir: Path, seed: int | None = None) -> Path:
    rho_targets = np.linspace(0, 2.5, 16)[1:]
    params = [
        {"b": 0.0, "remote_action": False},
        {"b": 0.56, "remote_action": False},
        {"b": 1.06, "remote_action": False},
    ]
    return run_velocity_density_experiment(
        "exp1",
        output_dir,
        rho_targets,
        params,
        include_remote_action=False,
        seed=seed,
    )


def run_exp2(output_dir: Path, seed: int | None = None) -> Path:
    rho_targets = np.linspace(0, 2.8, 20)[1:]
    params = [
        {"remote_action": False, "b": 0.56},
        {"remote_action": True, "b": 0.0},
        {"remote_action": True, "b": 0.56},
    ]
    return run_velocity_density_experiment(
        "exp2",
        output_dir,
        rho_targets,
        params,
        include_remote_action=True,
        seed=seed,
    )


def run_exp3(output_dir: Path, seed: int | None = None) -> Path:
    config: dict[str, Any] = dict(BASE_CONFIG)
    config.update(
        {
            "N": 20,
            "b": 0.56,
            "use_remote": True,
            "frames": 30,
            "frame_interval": 200,
        }
    )
    save_config(output_dir, "exp3", config)

    output_path = output_dir / "exp3.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("")

    rho, mean_velocity = simulate(
        N=int(config["N"]),
        L=float(config["L"]),
        dt=float(config["dt"]),
        T_relax=int(config["T_relax"]),
        T_measure=int(config["T_measure"]),
        a=float(config["a"]),
        b=float(config["b"]),
        tau=float(config["tau"]),
        v0_mean=float(config["v0_mean"]),
        v0_std=float(config["v0_std"]),
        use_remote=bool(config["use_remote"]),
        e=float(config["e"]),
        f=float(config["f"]),
        output_file=str(output_path),
        seed=seed,
    )
    print(
        f"rho: {rho:.2f}, b: {float(config['b']):.2f}, "
        f"mean_velocity: {mean_velocity:.4f}, remote_action: {bool(config['use_remote'])}"
    )
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run pedestrian flow experiments.")
    parser.add_argument(
        "--experiment",
        choices=["exp1", "exp2", "exp3", "all"],
        default="exp2",
        help="Experiment to run. Defaults to exp2 to preserve the original main.py behavior.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Directory for generated outputs.")
    parser.add_argument("--seed", type=int, default=None, help="Optional deterministic seed.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    experiments = ["exp1", "exp2", "exp3"] if args.experiment == "all" else [args.experiment]
    runners = {
        "exp1": run_exp1,
        "exp2": run_exp2,
        "exp3": run_exp3,
    }

    for experiment in experiments:
        runners[experiment](args.output_dir, args.seed)


if __name__ == "__main__":
    main()

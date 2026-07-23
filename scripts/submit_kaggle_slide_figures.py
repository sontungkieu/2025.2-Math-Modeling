from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ACCOUNT_PARSER = Path("/home/tung/.codex/skills/kaggle-job-ops/scripts/kaggle_accounts.py")


def run_command(
    cmd: list[str],
    *,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def accounts_file_default() -> Path:
    local = ROOT / ".secrets" / "all-kaggle.json"
    if local.exists():
        return local
    return Path("/home/tung/all-kaggle.json")


def load_kaggle_owners(accounts_file: Path) -> list[str]:
    result = run_command(
        [sys.executable, str(ACCOUNT_PARSER), "--accounts-file", str(accounts_file), "--list", "--json"],
        check=True,
    )
    records = json.loads(result.stdout)
    owners: list[str] = []
    for record in records:
        username = record.get("username")
        if username and username not in owners:
            owners.append(username)
    return owners


def materialize_kaggle_config(accounts_file: Path, owner: str, out_dir: Path) -> None:
    run_command(
        [
            sys.executable,
            str(ACCOUNT_PARSER),
            "--accounts-file",
            str(accounts_file),
            "--owner",
            owner,
            "--out-dir",
            str(out_dir),
        ],
        check=True,
    )


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:60].strip("-") or "math-modeling-slide-figures"


def copy_required_inputs(staging_dir: Path) -> None:
    staging_dir.mkdir(parents=True, exist_ok=True)


def notebook_json(args: argparse.Namespace) -> dict[str, Any]:
    text_files = {
        "plot_figures.py": (ROOT / "plot_figures.py").read_text(),
        "slides/math_modelling/generate_slide_figures.py": (
            ROOT / "slides" / "math_modelling" / "generate_slide_figures.py"
        ).read_text(),
    }
    command_args = [
        "slides/math_modelling/generate_slide_figures.py",
        "--force",
        "--skip-existing-output-copy",
        "--t-relax",
        str(args.t_relax),
        "--t-measure",
        str(args.t_measure),
        "--density-count",
        str(args.density_count),
        "--density-min",
        str(args.density_min),
        "--density-max",
        str(args.density_max),
        "--repeats",
        str(args.repeats),
        "--workers",
        str(args.workers),
    ]
    command_args_literal = repr(command_args)
    text_files_literal = repr(text_files)
    source = f"""
import json
import os
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

TEXT_FILES = {text_files_literal}

for relative_path, content in TEXT_FILES.items():
    target = Path(relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)

command = [sys.executable] + {command_args_literal}
print("Running:", " ".join(command))
env = dict(os.environ)
env["MPLBACKEND"] = "Agg"
subprocess.run(command, check=True, env=env)

slide_dir = Path("slides/math_modelling")
figure_paths = {{
    "body_length": slide_dir / "body_length.png",
}}
summary = {{
    "completed_at": datetime.now(timezone.utc).isoformat(),
    "command": command,
    "figures": {{name: str(path) for name, path in figure_paths.items() if path.exists()}},
    "generated_data": sorted(str(path) for path in (slide_dir / "generated_data").glob("*.csv")),
}}
Path("kaggle_run_summary.json").write_text(json.dumps(summary, indent=2))

with zipfile.ZipFile("generated_slide_figures.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for path in [
        slide_dir / "body_length.png",
        slide_dir / "generated_data" / "body_length.csv",
        Path("kaggle_run_summary.json"),
    ]:
        if path.exists():
            archive.write(path, path.as_posix())

print(json.dumps(summary, indent=2))
print("Wrote generated_slide_figures.zip")
""".strip()
    return {
        "cells": [
            {
                "cell_type": "code",
                "id": "generate-slide-figures",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [line + "\n" for line in source.splitlines()],
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write_kernel_metadata(staging_dir: Path, owner: str, slug: str, title: str, accelerator: str) -> None:
    metadata = {
        "id": f"{owner}/{slug}",
        "title": title,
        "code_file": "slide_figures_kaggle.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": accelerator == "gpu",
        "enable_tpu": accelerator == "tpu",
        "enable_internet": True,
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
    }
    (staging_dir / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2))


def status_fallback(owner: str, slug: str, env: dict[str, str]) -> dict[str, Any]:
    ref = f"{owner}/{slug}"
    status = run_command(["kaggle", "kernels", "status", ref], env=env, check=False)
    if status.returncode == 0:
        return {"method": "status", "returncode": 0, "stdout": status.stdout.strip(), "stderr": status.stderr.strip()}

    listing = run_command(["kaggle", "kernels", "list", "--mine", "--sort-by", "dateRun", "--csv"], env=env, check=False)
    found = ref in listing.stdout or slug in listing.stdout
    return {
        "method": "list-fallback",
        "returncode": listing.returncode,
        "found": found,
        "status_stderr": status.stderr.strip(),
        "list_stdout_head": "\n".join(listing.stdout.splitlines()[:8]),
        "list_stderr": listing.stderr.strip(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit the slide-figure generation job to Kaggle.")
    parser.add_argument("--accounts-file", type=Path, default=accounts_file_default(), help="Kaggle accounts file.")
    parser.add_argument("--owner", default=None, help="Kaggle username. Defaults to the first parsed account.")
    parser.add_argument("--status-ref", default=None, help="Only check status for an existing owner/slug notebook.")
    parser.add_argument("--download-ref", default=None, help="Only download output for an existing owner/slug notebook.")
    parser.add_argument(
        "--download-dir",
        type=Path,
        default=ROOT / "reports" / "kaggle_slide_figures_output",
        help="Directory used with --download-ref.",
    )
    parser.add_argument("--accelerator", choices=["gpu", "cpu", "tpu"], default="gpu", help="Kaggle accelerator.")
    parser.add_argument("--title", default=None, help="Kaggle notebook title.")
    parser.add_argument("--slug", default=None, help="Kaggle notebook slug.")
    parser.add_argument("--t-relax", type=int, default=80_000)
    parser.add_argument("--t-measure", type=int, default=80_000)
    parser.add_argument("--density-count", type=int, default=12)
    parser.add_argument("--density-min", type=float, default=0.25)
    parser.add_argument("--density-max", type=float, default=2.45)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--report-path", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Create staging files and report without pushing.")
    parser.add_argument("--keep-staging", action="store_true", help="Do not delete the temporary staging directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.accounts_file.exists():
        raise FileNotFoundError(f"Kaggle accounts file not found: {args.accounts_file}")
    if not ACCOUNT_PARSER.exists():
        raise FileNotFoundError(f"Kaggle account parser not found: {ACCOUNT_PARSER}")

    owners = load_kaggle_owners(args.accounts_file)
    if not owners:
        raise RuntimeError("No Kaggle owners found in accounts file.")
    existing_ref = args.status_ref or args.download_ref
    owner = args.owner or (existing_ref.split("/", 1)[0] if existing_ref and "/" in existing_ref else owners[0])
    if owner not in owners:
        raise ValueError(f"Owner {owner!r} is not present in {args.accounts_file}. Available: {', '.join(owners)}")

    if args.status_ref or args.download_ref:
        with tempfile.TemporaryDirectory(prefix="kaggle-config-") as config_dir:
            materialize_kaggle_config(args.accounts_file, owner, Path(config_dir))
            env = dict(os.environ)
            env["KAGGLE_CONFIG_DIR"] = config_dir

            result: dict[str, Any] = {"credential_owner": owner}
            if args.status_ref:
                if "/" not in args.status_ref:
                    raise ValueError("--status-ref must use the owner/slug format.")
                status_owner, status_slug = args.status_ref.split("/", 1)
                result["status_ref"] = args.status_ref
                result["status"] = status_fallback(status_owner, status_slug, env)

            if args.download_ref:
                if "/" not in args.download_ref:
                    raise ValueError("--download-ref must use the owner/slug format.")
                args.download_dir.mkdir(parents=True, exist_ok=True)
                output = run_command(
                    ["kaggle", "kernels", "output", args.download_ref, "-p", str(args.download_dir)],
                    env=env,
                    check=False,
                )
                downloaded_files = sorted(str(path) for path in args.download_dir.glob("*") if path.is_file())
                result["download_ref"] = args.download_ref
                result["download"] = {
                    "returncode": output.returncode,
                    "stdout": output.stdout.strip(),
                    "stderr": output.stderr.strip(),
                    "download_dir": str(args.download_dir),
                    "files": downloaded_files,
                }

        print(json.dumps(result, indent=2))
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    title = args.title or f"Math Modeling Slide Figures {timestamp}"
    slug = slugify(args.slug or title)
    report_path = args.report_path or ROOT / "reports" / f"kaggle_slide_figures_submit_{timestamp}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    kaggle_bin = shutil.which("kaggle")
    if not kaggle_bin and not args.dry_run:
        raise RuntimeError("kaggle CLI not found. Run with: uv run --with kaggle python scripts/submit_kaggle_slide_figures.py")

    staging_context: tempfile.TemporaryDirectory[str] | None = None
    if args.keep_staging:
        staging_dir = Path(tempfile.mkdtemp(prefix="kaggle-slide-figures-"))
    else:
        staging_context = tempfile.TemporaryDirectory(prefix="kaggle-slide-figures-")
        staging_dir = Path(staging_context.name)
    try:
        copy_required_inputs(staging_dir)
        (staging_dir / "slide_figures_kaggle.ipynb").write_text(json.dumps(notebook_json(args), indent=2))
        write_kernel_metadata(staging_dir, owner, slug, title, args.accelerator)

        report: dict[str, Any] = {
            "owner": owner,
            "ref": f"{owner}/{slug}",
            "title": title,
            "accelerator": args.accelerator,
            "staging_dir": str(staging_dir),
            "dry_run": args.dry_run,
            "parameters": {
                "t_relax": args.t_relax,
                "t_measure": args.t_measure,
                "density_count": args.density_count,
                "density_min": args.density_min,
                "density_max": args.density_max,
                "repeats": args.repeats,
                "workers": args.workers,
            },
        }

        if not args.dry_run:
            with tempfile.TemporaryDirectory(prefix="kaggle-config-") as config_dir:
                materialize_kaggle_config(args.accounts_file, owner, Path(config_dir))
                env = dict(os.environ)
                env["KAGGLE_CONFIG_DIR"] = config_dir
                push = run_command(["kaggle", "kernels", "push", "-p", str(staging_dir)], env=env, check=False)
                report["push"] = {
                    "returncode": push.returncode,
                    "stdout": push.stdout.strip(),
                    "stderr": push.stderr.strip(),
                }
                if push.returncode != 0:
                    report_path.write_text(json.dumps(report, indent=2))
                    raise RuntimeError(f"kaggle push failed; see report: {report_path}")
                report["status"] = status_fallback(owner, slug, env)

        report_path.write_text(json.dumps(report, indent=2))
        print(f"ref={owner}/{slug}")
        print(f"report={report_path}")
        if args.dry_run or args.keep_staging:
            print(f"staging_dir={staging_dir}")
        else:
            report["staging_dir"] = None
            report_path.write_text(json.dumps(report, indent=2))
    finally:
        if staging_context is not None:
            staging_context.cleanup()


if __name__ == "__main__":
    main()

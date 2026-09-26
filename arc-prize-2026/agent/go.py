"""One command: build the notebook, push it to Kaggle, and watch Phase A.

    python3 go.py                  # m2 variant, smoke Phase A
    python3 go.py --variant base   # the unchanged B81 fallback
    python3 go.py --status         # only report the status of the last push

Finds your Kaggle username from ~/.kaggle/kaggle.json (or KAGGLE_USERNAME). If Kaggle rejects the pinned
docker image, retries once without it. It never submits; after Phase A finishes, submit from the notebook page.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def username() -> str:
    if os.environ.get("KAGGLE_USERNAME"):
        return os.environ["KAGGLE_USERNAME"]
    cfg = Path(os.environ.get("KAGGLE_CONFIG_DIR", Path.home() / ".kaggle")) / "kaggle.json"
    if cfg.is_file():
        return json.loads(cfg.read_text())["username"]
    sys.exit("No Kaggle username found. Create a token at kaggle.com -> Settings -> API -> Create New Token,\n"
             "save it as ~/.kaggle/kaggle.json, or run: KAGGLE_USERNAME=<name> python3 go.py")


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    print("$ " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=("m2", "m3", "lean", "base"), default="m2")
    ap.add_argument("--phase-a", choices=("smoke", "full"), default="smoke")
    ap.add_argument("--run", default="1")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    user = username()
    slug = f"arc3-{args.variant}-{args.phase_a}-r{args.run}"
    ref = f"{user}/{slug}"
    if not args.status:
        subprocess.run([sys.executable, str(HERE / "build_notebook.py"), "--variant", args.variant, "--owner", user,
                        "--phase-a", args.phase_a, "--run", args.run], check=True)
        out = HERE / "out" / slug
        push = run(["kaggle", "kernels", "push", "-p", str(out)])
        print(push.stdout + push.stderr)
        if push.returncode != 0 or "error" in (push.stdout + push.stderr).lower():
            meta_path = out / "kernel-metadata.json"
            meta = json.loads(meta_path.read_text())
            if meta.pop("docker_image", None):
                print("Push failed; retrying without the pinned docker_image ...")
                meta_path.write_text(json.dumps(meta, indent=2))
                push = run(["kaggle", "kernels", "push", "-p", str(out)])
                print(push.stdout + push.stderr)
            if push.returncode != 0:
                sys.exit("Push failed. Paste everything above to Claude.")
        print(f"\nPushed https://www.kaggle.com/code/{ref}\n"
              "Open it once: confirm the accelerator is 'GPU RTX Pro 6000' and internet is OFF.\n")

    # Phase A takes ~40 min (smoke) or ~2.5 h (full); poll every 5 minutes.
    while True:
        status = run(["kaggle", "kernels", "status", ref])
        text = (status.stdout + status.stderr).strip()
        print(time.strftime("%H:%M:%S"), text, flush=True)
        low = text.lower()
        if "complete" in low:
            print("\nPhase A finished. Checking the log for our markers ...")
            logdir = HERE / "out" / f"logs-{slug}"
            run(["kaggle", "kernels", "output", ref, "-p", str(logdir)])
            blob = "".join(p.read_text(errors="ignore") for p in logdir.glob("*.log")) if logdir.exists() else ""
            marks = ["THUI_A5_PROFILE ok",
                     "OURS_GRAFTS none" if args.variant == "base" else f"OURS_GRAFTS ok variant={args.variant}"]
            if args.variant in ("m2", "m3", "lean"):
                marks += ["OURS_NOTE_FILL ok"]
            if args.variant in ("m2", "m3"):
                marks += ["OURS_PROMPT_EXTRAS ok"]
            if args.variant == "m3":
                marks += ["OURS_KEEP_ON_DEATH ok"]
            for m in marks:
                print(("  OK      " if m in blob else "  MISSING ") + m)
            for line in blob.split('"data":"'):
                if line.startswith("[finished]"):
                    print("  " + line.split("note=")[0])
            print(f"  (full log in {logdir})")
            print(f"\nIf all OK: open https://www.kaggle.com/code/{ref} -> 'Submit to Competition' -> submission.parquet.")
            return
        if "error" in low or "cancel" in low:
            sys.exit(f"Phase A failed. Open https://www.kaggle.com/code/{ref}, copy the last ~50 log lines to Claude.")
        time.sleep(300)


if __name__ == "__main__":
    main()

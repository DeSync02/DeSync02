#!/usr/bin/env python3
"""
Generate a repository with backdated commits to form a 53x7 contribution pattern.
Usage example (PowerShell):
  python .\generate_wreck_it_ralph_graph.py --git-name "Your Name" --git-email "you@example.com" --repo wreck-it-ralph-graph --text "WRECK IT RALPH"
Optionally provide --remote to have the script add a remote; pushing will still prompt for credentials.
"""
import os
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

GRID_W = 53
GRID_H = 7
BRANCH = "main"

def run(cmd, cwd=None, env=None):
    print(">", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, env=env or os.environ, check=True)

def render_text_to_grid(text, grid_w=GRID_W, grid_h=GRID_H):
    # Create a grayscale canvas; attempt to use a TTF font if available.
    cell_px = 12
    img_w = grid_w * cell_px
    img_h = grid_h * cell_px
    image = Image.new("L", (img_w, img_h), 255)
    draw = ImageDraw.Draw(image)

    # Try common font locations (Windows + Linux); fallback to default bitmap font
    font = None
    for p in [
        "C:\\Windows\\Fonts\\Arial.ttf",
        "C:\\Windows\\Fonts\\Tahoma.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        try:
            if os.path.exists(p):
                font = ImageFont.truetype(p, int(cell_px * 3))
                break
        except Exception:
            font = None
    if font is None:
        font = ImageFont.load_default()

    # Draw centered text
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = max(0, (img_w - tw) // 2)
    y = max(0, (img_h - th) // 2)
    draw.text((x, y), text, fill=0, font=font)

    # Map to grid cells (1 = dark => commit, 0 = light => no commit)
    cells = [[0 for _ in range(grid_w)] for _ in range(grid_h)]
    for gy in range(grid_h):
        for gx in range(grid_w):
            px = int((gx + 0.5) * (img_w / grid_w))
            py = int((gy + 0.5) * (img_h / grid_h))
            v = image.getpixel((px, py))
            cells[gy][gx] = 1 if v < 200 else 0
    return cells

def build_dates_from_cells(cells):
    today = datetime.today().date()
    start_date = today - timedelta(days=364)  # cover ~last year
    dates = []
    for week in range(GRID_W):
        for day in range(GRID_H):
            if cells[day][week]:
                d = start_date + timedelta(weeks=week, days=day)
                if d <= today:
                    dates.append(d)
    return sorted(set(dates))

def create_repo_and_commits(repo_name, git_name, git_email, dates, text):
    repo_dir = Path(repo_name).resolve()
    repo_dir.mkdir(parents=True, exist_ok=True)
    # create a marker file that will be modified across commits
    (repo_dir / "README.md").write_text(f"# {repo_name}\n\nGenerated contribution pattern: {text}\n")

    run(["git", "init"], cwd=str(repo_dir))
    run(["git", "checkout", "-B", BRANCH], cwd=str(repo_dir))
    run(["git", "config", "user.name", git_DeSync02], cwd=str(repo_dir))
    run(["git", "config", "user.email", git_solis.vincent002@gmail.com], cwd=str(repo_dir))

    # Ensure there's at least one initial commit
    run(["git", "add", "README.md"], cwd=str(repo_dir))
    env = os.environ.copy()
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT12:00:00+00:00")
    env["GIT_AUTHOR_DATE"] = now_iso
    env["GIT_COMMITTER_DATE"] = now_iso
    run(["git", "commit", "-m", "Initial README"], cwd=str(repo_dir), env=env)

    # Create a small file per-date and commit with backdated timestamps
    for d in dates:
        fn = f"contrib_{d.isoformat()}.txt"
        p = repo_dir / fn
        p.write_text(f"Contribution for {d.isoformat()}\n")
        run(["git", "add", fn], cwd=str(repo_dir))
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = f"{d.isoformat()}T12:00:00+00:00"
        env["GIT_COMMITTER_DATE"] = env["GIT_AUTHOR_DATE"]
        run(["git", "commit", "-m", f"Contrib {d.isoformat()}"], cwd=str(repo_dir), env=env)

    # Final add/commit touch so repo is clean
    run(["git", "add", "README.md"], cwd=str(repo_dir))
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = datetime.utcnow().strftime("%Y-%m-%dT12:00:00+00:00")
    env["GIT_COMMITTER_DATE"] = env["GIT_AUTHOR_DATE"]
    run(["git", "commit", "-m", "Finalize"], cwd=str(repo_dir), env=env)

    print("\nRepository created at:", repo_dir)
    return repo_dir

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--git-name", required=True, help="Git author name")
    parser.add_argument("--git-email", required=True, help="Git author email (must be verified on GitHub)")
    parser.add_argument("--repo", default="wreck-it-ralph-graph", help="Local repo folder name")
    parser.add_argument("--text", default="WRECK IT RALPH", help="Text to render into the contribution grid")
    parser.add_argument("--remote", default=None, help="Remote URL to add (optional)")
    args = parser.parse_args()

    print("Rendering text to grid...")
    cells = render_text_to_grid(args.text)
    dates = build_dates_from_cells(cells)
    print(f"Planned commits on {len(dates)} dates (will create one commit per active cell).")
    repo_dir = create_repo_and_commits(args.repo, args.git_name, args.git_email, dates, args.text)

    if args.remote:
        run(["git", "remote", "add", "origin", args.remote], cwd=str(repo_dir))
        print("Remote added. To push run:")
        print(f"  cd {repo_dir}")
        print(f"  git push -u origin {BRANCH}")
    else:
        print("No remote provided. To publish, create a public repo on GitHub, then:")
        print(f"  cd {repo_dir}")
        print("  git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git")
        print(f"  git push -u origin {BRANCH}")

if __name__ == "__main__":
    main()
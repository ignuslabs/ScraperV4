import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

def run(cmd, cwd=None, check=True):
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result

def safe_title_from_file(md_path: Path) -> str:
    # If file has a first-level heading, use it; else use filename without extension
    try:
        with md_path.open('r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    # take first heading text after leading #'s
                    return line.lstrip('#').strip()
    except Exception:
        pass
    return md_path.stem.replace('-', ' ').replace('_', ' ').strip()

def make_home_md(wiki_dir: Path, title: str, intro: str):
    home = wiki_dir / "Home.md"
    content = f"# {title}\n\n{intro}\n"
    home.write_text(content, encoding='utf-8')

def make_sidebar_md(wiki_dir: Path):
    sidebar = wiki_dir / "_Sidebar.md"

    # gather pages (exclude meta files)
    pages = []
    for p in sorted(wiki_dir.glob("*.md")):
        if p.name in {"Home.md", "_Sidebar.md", "_Footer.md"}:
            continue
        pages.append(p)

    # Build a bullet list using wiki-style links [[Page Name]]
    lines = ["## Pages", ""]
    for p in pages:
        display = safe_title_from_file(p)
        page_name = p.stem  # GitHub wiki treats [[Stem]] as link to page (no .md)
        # If filename has spaces/dashes, the wiki resolves it; keep it simple
        lines.append(f"- [[{page_name}|{display}]]")
    lines.append("")
    sidebar.write_text("\n".join(lines), encoding='utf-8')

def ensure_master_branch(wiki_dir: Path):
    # Check current branch; if none or different, create/switch to master
    try:
        current = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=wiki_dir, check=False)
        branch = (current.stdout or "").strip()
    except Exception:
        branch = ""

    if branch == "master":
        return

    # If no commits yet, create master
    has_commits = run(["git", "rev-parse", "--verify", "HEAD"], cwd=wiki_dir, check=False).returncode == 0
    if has_commits:
        # If some other branch, try to checkout master or create it tracking origin
        ret = run(["git", "checkout", "master"], cwd=wiki_dir, check=False)
        if ret.returncode != 0:
            # Create master from current
            run(["git", "checkout", "-b", "master"], cwd=wiki_dir)
    else:
        # orphan initial master if totally empty
        run(["git", "checkout", "-b", "master"], cwd=wiki_dir)

def main():
    parser = argparse.ArgumentParser(description="Bulk upload Markdown files to a GitHub Wiki with Home.md and _Sidebar.md.")
    parser.add_argument("--repo", required=True, help="Repo in form owner/name (e.g., ignuslabs/ScraperV4)")
    parser.add_argument("--source", required=True, help="Path to folder containing .md files to upload")
    parser.add_argument("--workdir", default="", help="Optional path to clone the wiki into; defaults to temp dir")
    parser.add_argument("--title", default="Project Wiki", help="Title for Home.md")
    parser.add_argument("--intro", default="Welcome to the project wiki.", help="Intro paragraph for Home.md")
    parser.add_argument("--clean", action="store_true", help="Clean wiki dir before copying (removes existing .md files)")
    args = parser.parse_args()

    repo_slug = args.repo.strip()
    if "/" not in repo_slug:
        print("Error: --repo must be in the form owner/name", file=sys.stderr)
        sys.exit(1)

    source_dir = Path(args.source).expanduser().resolve()
    if not source_dir.is_dir():
        print(f"Error: --source '{source_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)

    # Prepare working directory
    own_tmp = False
    if args.workdir:
        base_dir = Path(args.workdir).expanduser().resolve()
        base_dir.mkdir(parents=True, exist_ok=True)
    else:
        base_dir = Path(tempfile.mkdtemp(prefix="wiki_push_"))
        own_tmp = True

    wiki_url = f"https://github.com/{repo_slug}.wiki.git"
    wiki_dir = base_dir / f"{repo_slug.split('/')[-1]}.wiki"

    # Clone or update the wiki repository
    if wiki_dir.exists() and (wiki_dir / ".git").exists():
        # Existing clone: fetch latest
        run(["git", "fetch", "origin"], cwd=wiki_dir)
        run(["git", "remote", "-v"], cwd=wiki_dir)
    else:
        run(["git", "clone", wiki_url, str(wiki_dir)])

    # Ensure we're on master (GitHub Wikis use master)
    ensure_master_branch(wiki_dir)

    # Sync from origin/master if it exists
    run(["git", "pull", "origin", "master"], cwd=wiki_dir, check=False)

    # Optionally clean existing .md files (not images/attachments)
    if args.clean:
        for p in wiki_dir.glob("*.md"):
            p.unlink(missing_ok=True)

    # Copy all .md files from source
    copied = 0
    for p in source_dir.glob("*.md"):
        dest = wiki_dir / p.name
        shutil.copy2(p, dest)
        copied += 1

    if copied == 0:
        print("No .md files found in source directory; nothing to do.")
        if own_tmp:
            shutil.rmtree(base_dir, ignore_errors=True)
        sys.exit(0)

    # Create/overwrite Home.md and _Sidebar.md
    make_home_md(wiki_dir, args.title, args.intro)
    make_sidebar_md(wiki_dir)

    # Stage, commit, push
    run(["git", "add", "."] , cwd=wiki_dir)
    # Avoid empty commit error
    status = run(["git", "status", "--porcelain"], cwd=wiki_dir)
    if status.stdout.strip():
        run(["git", "commit", "-m", "Update wiki pages, Home.md, and _Sidebar.md"], cwd=wiki_dir)
        # If the remote doesn't have master yet, this creates it
        run(["git", "push", "origin", "master"], cwd=wiki_dir)
        print("✅ Pushed to wiki master branch.")
    else:
        print("No changes detected; nothing to commit.")

    if own_tmp:
        print(f"(Temporary working directory kept at: {base_dir})")

if __name__ == "__main__":
    main()
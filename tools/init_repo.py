import argparse
import os
from pathlib import Path
import shutil
from typing import Final
import subprocess

from bazel_tools.tools.python.runfiles import runfiles
from rich import print as rprint

TEMPLATE_DIR: Final = 'template'

COPY_PATHS: Final = [
    '.aspect',
    'third_party',
    'tools',
    '.bazeliskrc',
    '.clang-format',
    '.clang-tidy',
    '.ruff.toml',
]

APPEND_PATHS: Final = [
    '.gitignore',
    'BUILD',
    'MODULE.bazel',
]

BEGIN_DELIMITER: Final = '# BEGIN ==================== lint_it_all ====================\n'
END_DELIMITER: Final = '# END ==================== lint_it_all ====================\n'


def git_is_available() -> bool:
    try:
        subprocess.check_output('git --version'.split(), encoding='utf-8')
        return True
    except subprocess.CalledProcessError:
        return False


def in_git_repo(cwd: Path) -> bool:
    try:
        return subprocess.check_output(
            'git rev-parse --is-inside-work-tree'.split(),
            encoding='utf-8',
            cwd=cwd).strip().lower() == 'true'
    except subprocess.CalledProcessError:
        return False


def git_is_clean(cwd: Path) -> bool:
    return subprocess.check_output(
        'git ls-files --others --modified --exclude-standard'.split(),
        encoding='utf-8',
        cwd=cwd).strip() == ''


def get_workspace_path() -> Path:
    return Path(os.environ['BUILD_WORKSPACE_DIRECTORY'])


def get_root_from_this(this: str) -> Path:
    r = runfiles.Create()
    path = r.Rlocation(this)
    if not path:
        raise FileNotFoundError(this)
    return Path(path).parents[1]


def update_from_template(src: Path, dest: Path, name: str) -> None:
    if not dest.exists():
        dest.touch()

    dest_lines: list[str] = dest.open('r').readlines()

    start_ind = None
    end_ind = None
    for i, line in enumerate(dest_lines):
        if line == BEGIN_DELIMITER:
            if start_ind is not None:
                rprint(
                    f'[red]Duplicate lint_it_all delimiters found. Skipping {name}'
                )
                return
            start_ind = i
        if line == END_DELIMITER:
            if end_ind is not None:
                rprint(
                    f'[red]Duplicate lint_it_all delimiters found. Skipping {name}'
                )
                return
            end_ind = i

    # Template is not present.
    if start_ind is None and end_ind is None:
        if dest_lines and dest_lines[-1].strip() != '':
            dest_lines.append('\n')
        dest_lines.append(BEGIN_DELIMITER)
        dest_lines.extend(src.open('r').readlines())
        dest_lines.append(END_DELIMITER)
    # Template is replaced.
    elif start_ind is not None and end_ind is not None:
        dest_lines = dest_lines[:start_ind + 1] + src.open(
            'r').readlines() + dest_lines[end_ind:]
    # Mismatched delimiters.
    else:
        rprint(
            f'[red]Mismatched lint_it_all delimiters found. Skipping {name}')
        return

    dest.open('w').writelines(dest_lines)
    rprint(f'[blue]Updated template in {name}')


def init_repo(src_root: Path, dest_root: Path) -> None:
    for p in COPY_PATHS:
        src = src_root / TEMPLATE_DIR / p
        dest = dest_root / p

        dest.parent.mkdir(parents=True, exist_ok=True)

        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copyfile(src, dest)

        rprint(f'[blue]Copied {p}')

    for p in APPEND_PATHS:
        src = src_root / TEMPLATE_DIR / p
        dest = dest_root / p
        update_from_template(src, dest, p)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Copy linting and formatting config to current repo.')

    parser.add_argument("--this",
                        required=True,
                        help='The $(rlocation) of this file.')

    args = parser.parse_args()

    workspace_path = get_workspace_path()

    if not git_is_available():
        rprint('[red]Git not present. Aborting')
        return

    if not in_git_repo(workspace_path):
        rprint('[red]Not inside git repository. Aborting')
        return

    if not git_is_clean(workspace_path):
        rprint(
            '[red]Unstaged changes detected. Stage or commit changes to continue.'
        )
        return

    init_repo(get_root_from_this(args.this), workspace_path)


if __name__ == '__main__':
    main()

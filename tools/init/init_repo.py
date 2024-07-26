import argparse
import os
import pathlib
import shutil

from bazel_tools.tools.python.runfiles import runfiles


def get_workspace() -> pathlib.Path:
    return pathlib.Path(os.environ['BUILD_WORKSPACE_DIRECTORY'])


def get_root_from_this(this: str) -> pathlib.Path:
    r = runfiles.Create()
    path = r.Rlocation(this)
    if not path:
        raise FileNotFoundError(this)
    return pathlib.Path(path).parents[2]


def copy_init_files(root: pathlib.Path) -> None:
    workspace_path = get_workspace()

    srcs = [
        '.aspect',
        'tools/format',
        'tools/lint',
        '.bazeliskrc',
        '.clang-format',
        '.clang-tidy',
    ]
    for rel_path in srcs:
        src = root / pathlib.Path(rel_path)
        dest = workspace_path / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copy(src, dest)
        print(f'Copied {rel_path}')


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Copy linting and formatting config to current repo.')

    parser.add_argument("--this",
                        required=True,
                        help='The $(rlocation) of this file.')

    args = parser.parse_args()

    copy_init_files(get_root_from_this(args.this))


if __name__ == '__main__':
    main()

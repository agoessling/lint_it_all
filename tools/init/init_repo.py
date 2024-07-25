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


def get_init_file_paths(rel_paths: list[str]) -> list[pathlib.Path]:
    output = []

    r = runfiles.Create()
    for rel_path in rel_paths:
        abs_path = r.Rlocation(rel_path)
        if not abs_path:
            raise FileNotFoundError(rel_path)
        output.append(pathlib.Path(abs_path))

    return output


def copy_init_files(files: list[pathlib.Path], root: pathlib.Path) -> None:
    workspace_path = get_workspace()
    for file in files:
        rel_path = file.relative_to(root)
        dest = workspace_path / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, dest)
        print(f'Copied {rel_path}')


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Copy linting and formatting config to current repo.')

    parser.add_argument("--init_files", nargs='+', required=True, help='Files to copy to repo.')
    parser.add_argument("--this", required=True, help='The $(rlocation) of this file.')

    args = parser.parse_args()

    copy_init_files(get_init_file_paths(args.init_files), get_root_from_this(args.this))


if __name__ == '__main__':
    main()

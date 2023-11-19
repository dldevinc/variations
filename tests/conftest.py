from pathlib import Path


def pytest_addoption(parser):
    parser.addoption("--folder", action="store")


def pytest_generate_tests(metafunc):
    """
    @pytest.mark.iterdir("file", "tests/input/processors")
    @pytest.mark.parametrize("x", [4, 5, 6])
    def test_file(file, x):
        ...
    """
    if hasattr(metafunc.function, "pytestmark"):
        for mark in metafunc.function.pytestmark:
            if mark.name == "iterdir":
                paths = mark.args[1]
                if isinstance(paths, str):
                    paths = [paths]

                files = []
                for path in paths:
                    root = Path(path).resolve()
                    if not root.is_dir():
                        raise RuntimeError(f"{root} is not folder")

                    files.extend(
                        sorted(file for file in root.iterdir() if file.is_file())
                    )

                metafunc.parametrize(
                    mark.args[0],
                    files,
                    ids=map(str, files)
                )

from pathlib import Path

from . import helper


def pytest_generate_tests(metafunc):
    if hasattr(metafunc.cls, "input_files"):
        if "input_file" in metafunc.fixturenames:
            argvalues = []
            for dirname in metafunc.cls.input_files:
                resolved_path = (Path(helper.INPUT_PATH) / dirname).resolve()
                if resolved_path.is_dir():
                    sorted_files = sorted(file for file in resolved_path.iterdir() if file.is_file())
                    argvalues.extend(
                        file.relative_to(helper.INPUT_PATH)
                        for file in sorted_files
                    )

            metafunc.parametrize(
                "input_file",
                argvalues,
                ids=map(str, argvalues)
            )

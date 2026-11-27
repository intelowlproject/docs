# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterator, List, Set, Tuple

from django.test import SimpleTestCase

SETTINGS_DIR = Path(__file__).resolve().parents[2] / "intel_owl" / "settings"
SETTINGS_INIT = SETTINGS_DIR / "__init__.py"


def _assigned_names(node: ast.AST) -> Iterator[Tuple[str, int]]:
    """Names bound by a module-level assignment, including inside if/try blocks (where settings are
    conditionally defined). Function and class bodies are skipped: their locals are not settings."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(child, ast.Assign):
            for target in child.targets:
                if isinstance(target, ast.Name):
                    yield target.id, child.lineno
        elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            yield child.target.id, child.lineno
        yield from _assigned_names(child)


def _wildcard_imported_modules() -> List[str]:
    """The submodule names __init__.py pulls in with `from .x import *`, in source order."""
    tree = ast.parse(SETTINGS_INIT.read_text())
    return [
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names)
    ]


class SettingsSingleSourceTestCase(SimpleTestCase):
    """intel_owl/settings/__init__.py pulls every submodule in with a wildcard import, so a name
    assigned in two of them silently resolves to whichever module is imported last. Re-ordering
    those lines then changes the deployment's behaviour, which is exactly how CHATBOT_QUEUE ended
    up ignoring its environment variable. One assignment per setting removes the ordering
    dependency altogether."""

    def test_no_setting_is_assigned_in_two_wildcard_imported_modules(self):
        # __init__.py assigns settings of its own (INSTALLED_APPS, TEST_RUNNER) before the wildcard
        # block, and a submodule shadowing one of those is the same bug in the other direction
        sources: Dict[str, Path] = {SETTINGS_INIT.name: SETTINGS_INIT}
        for module in _wildcard_imported_modules():
            module_path = SETTINGS_DIR / f"{module}.py"
            self.assertTrue(
                module_path.is_file(),
                msg=f"cannot audit the wildcard import of .{module}: {module_path} is not a file",
            )
            sources[module_path.name] = module_path

        origins: Dict[str, Set[str]] = defaultdict(set)
        for name, path in sources.items():
            for setting, lineno in _assigned_names(ast.parse(path.read_text())):
                origins[setting].add(f"{name}:{lineno}")

        shadowed = {
            setting: sorted(locations)
            for setting, locations in origins.items()
            # locations within a single module are re-assignments, not shadowing
            if len({location.split(":")[0] for location in locations}) > 1
        }

        self.assertEqual(
            shadowed,
            {},
            msg="these settings are assigned in more than one module of intel_owl/settings, so "
            "their value depends on the import order in intel_owl/settings/__init__.py",
        )

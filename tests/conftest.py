from pathlib import Path
import sys

import pytest


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))


_REPEATABILITY_CHAIN_PREFIX = "test_public_av_return_replication_repeatability_"


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Run inherited chain tests only where each test method is defined."""
    kept: list[pytest.Item] = []
    deselected: list[pytest.Item] = []
    for item in items:
        path = Path(str(item.path))
        test_class = getattr(item, "cls", None)
        is_repeatability_chain = path.stem.startswith(_REPEATABILITY_CHAIN_PREFIX)
        method_defined_here = test_class is None or item.name in test_class.__dict__
        if is_repeatability_chain and not method_defined_here:
            deselected.append(item)
        else:
            kept.append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = kept

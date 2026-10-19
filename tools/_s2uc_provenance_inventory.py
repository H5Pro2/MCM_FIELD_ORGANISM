"""Complete union for isolated provenance development; leaves V9 admission intact."""
import ast
from tools import _s2uc_source_execution_binding as baseline

TEST = 'tests/test_s2uc_provenance_evaluation.py'
ADDITIONS = ('tools/_s2uc_provenance_evaluation.py', 'tools/_s2uc_provenance_inventory.py',
             'tools/s2uc_provenance_check.py', TEST)
ENTRIES = baseline.ENTRIES + ADDITIONS


def current():
    value = baseline.discovery._collect(baseline.discovery.ROOT, ENTRIES, 's2uc.provenance-inventory.v1')
    value['external']['native_runtime'] = baseline.current()['external']['native_runtime']
    return value


def test_ids():
    _, data, _ = baseline.discovery.read_file(baseline.discovery.ROOT, TEST)
    added = [f"{TEST[:-3].replace('/', '.')}.{cls.name}.{method.name}" for cls in ast.parse(data).body
             if isinstance(cls, ast.ClassDef) for method in cls.body
             if isinstance(method, ast.FunctionDef) and method.name.startswith('test_')]
    return sorted(baseline.test_ids() + added)

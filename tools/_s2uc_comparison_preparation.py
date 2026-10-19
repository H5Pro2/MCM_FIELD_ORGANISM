import ast
import json
from pathlib import Path
from tools import _s2uc_provenance_appendix as old
from tools import _s2uc_preparation_resources as resources

ROOT = old.b.discovery.ROOT
VERSION = 's2uc.comparison-preparation.p1'
TEST = 'tests/test_s2uc_comparison_preparation.py'
ENTRIES = old.ENTRIES + ('tools/_s2uc_comparison_preparation.py', TEST,
                        'tools/s2uc_preparation_check.py')
AUTH = {'scope': 'PREPARATION_ONLY', 'real_execution_authorized': False,
        'formal_qualification': False}
NAMES = {'preparation.json', 'source-context.json', 'resources.json',
         'protocol.json', 'ledger.json'}
canonical = old.b.old.canonical
need = old.need

def current():
    inv = old.b.discovery._collect(ROOT, ENTRIES, VERSION)
    inv['external']['native_runtime'] = old.b.current()['external']['native_runtime']
    return inv

def test_ids():
    tree = ast.parse((ROOT / TEST).read_bytes())
    return sorted(old.test_ids() + [f'{TEST[:-3].replace("/", ".")}.{c.name}.{m.name}'
                  for c in tree.body if isinstance(c, ast.ClassDef)
                  for m in c.body if isinstance(m, ast.FunctionDef) and m.name.startswith('test_')])

def reference(path):
    name = Path(path).absolute().relative_to(ROOT).as_posix()
    return old.b.discovery.read_file(ROOT, name)[0]

def _read(ref, loaded):
    actual, data, identity = old.b.discovery.read_file(ROOT, ref['path'])
    need(actual == ref, 'P1_REFERENCE_CHANGED')
    for path, (_, other) in loaded.items():
        need(path == ref['path'] or identity != other, 'P1_FILE_ALIAS')
    loaded[ref['path']] = (data, identity)
    return json.loads(data)

def _compatible(prior, inv):
    rows = {r['path']: r for r in inv['files']}
    need(len({r['path'] for r in prior['files']}) == len(prior['files'])
         and all(rows.get(r['path']) == r for r in prior['files']), 'P1_STALE_CODE')
    need(prior['code_bytes'] == sum(r['bytes'] for r in prior['files']), 'P1_CODE_COUNT')
    for key in ('interpreter', 'distributions', 'native_runtime'):
        need(prior['external'][key] == inv['external'][key], 'P1_STALE_RUNTIME')
    need(all(r in inv['external']['modules'] for r in prior['external']['modules']),
         'P1_STALE_RUNTIME')

def _coverage(groups, inv, loaded):
    mapped = {}
    for index, group in enumerate(groups):
        need(set(group) == {'result', 'inventory'}, 'P1_GROUP_SCHEMA')
        result = _read(group['result'], loaded)
        prior = _read(group['inventory'], loaded)
        _compatible(prior, inv)
        required = dict(formal_qualification=False, real_execution_authorized=False,
                        code_unchanged=True, expected_ids_complete=True,
                        exit_code=0, errors=0, failures=0, skips=0)
        need(all(type(result.get(k)) is type(v) and result[k] == v
                 for k, v in required.items()), 'P1_RESULT_INVALID')
        pin = result.get('inventory', {})
        need(pin.get('sha256') == group['inventory']['sha256']
             and pin.get('bytes') == group['inventory']['bytes'], 'P1_RESULT_INVENTORY')
        ids = result['test_ids']
        need(type(ids) is list and len(ids) == len(set(ids)) == result['tests_run']
             and set(ids) == set(result['results'])
             and all(v == 'PASS' for v in result['results'].values()), 'P1_RESULT_IDS')
        paths = {r['path'] for r in prior['files']}
        need(all(n.rsplit('.', 2)[0].replace('.', '/') + '.py' in paths for n in ids),
             'P1_UNBOUND_TEST_CODE')
        for name in ids:
            need(name not in mapped, 'P1_DUPLICATE_TEST')
            mapped[name] = index
    need(sorted(mapped) == test_ids(), 'P1_MISSING_TEST_OBLIGATION')
    prefixes = sorted({name.rsplit('.', 1)[0] for name in mapped})
    return {'version': VERSION, 'groups': groups, 'prefixes': prefixes,
            'rows': [[prefixes.index(name.rsplit('.', 1)[0]), name.rsplit('.', 1)[1],
                      mapped[name], 'PASS'] for name in sorted(mapped)],
            'separate_executions': True}

def _binding(folder, inventory, inv):
    science = old.b.context.run_binding
    return {'version': VERSION, 'authority': AUTH,
            'run_id': science.PREPARED_RUN_ID, 'output': science.PREPARED_OUTPUT,
            'inventory': inventory, 'context': reference(folder / 'source-context.json'),
            'resources': reference(folder / 'resources.json'), 'protocol': reference(folder / 'protocol.json'),
            'nu_plan': reference(ROOT / old.b.old.NU_PLAN),
            'evaluation': [r for r in inv['files'] if r['path'] in
                           ('tools/_s2uc_provenance_evaluation.py', 'tools/_s2uc_provenance_appendix.py',
                            'tools/_s2uc_run_binding.py', 'tools/_s2uc_evaluation.py')]}

def _evaluate(folder, inv):
    folder = Path(folder)
    need({p.name for p in folder.iterdir()} == NAMES, 'P1_UNREGISTERED_FILE')
    loaded = {}
    def local(name):
        return _read(reference(folder / name), loaded)
    binding = local('preparation.json')
    need(binding == _binding(folder, binding.get('inventory'), inv), 'P1_BINDING_INVALID')
    need(not (ROOT / binding['output']).exists(), 'P1_OUTPUT_EXISTS')
    context = _read(binding['context'], loaded)
    old.b.context.validate_source_context(context)
    _read(binding['nu_plan'], loaded)
    need(binding['nu_plan']['sha256']==context['source_plan_sha256'],'P1_PLAN_HASH')
    need(_read(binding['resources'], loaded) == resources.contract(), 'P1_RESOURCES_CHANGED')
    need(_read(binding['inventory'], loaded) == inv, 'P1_CURRENT_INVENTORY')
    need(binding['inventory']['bytes'] <= 16384, 'P1_INVENTORY_LIMIT')
    protocol = _read(binding['protocol'], loaded)
    need(binding['protocol']['bytes'] <= 32768, 'P1_PROTOCOL_LIMIT')
    need(protocol == _coverage(protocol['groups'], inv, loaded), 'P1_PROTOCOL_MISMATCH')
    ledger = local('ledger.json')
    amounts = {k: 0 for k in old.b.resources.CATEGORIES}
    amounts['code'] = inv['code_bytes']
    metadata = {reference(folder / n)['path'] for n in ('preparation.json', 'source-context.json')}
    files = []
    for path, (data, _) in sorted(loaded.items()):
        category = 'metadata' if path in metadata else 'static_shared'
        amounts[category] += len(data)
        files.append({'path': path, 'bytes': len(data), 'category': category})
    actual = resources.account(amounts)
    need(actual['within_limits'], 'P1_BUDGET_EXCEEDED:' + ','.join(actual['violations']))
    expected = {'version': VERSION, 'files': files, 'actual': actual,
                'scope': 'PREPARATION_ONLY_NO_PRODUCT_OR_OBSERVER',
                'code_inventory_sha256': binding['inventory']['sha256']}
    return expected, ledger, len(protocol['rows'])

def read(folder):
    expected, ledger, count = _evaluate(folder, current())
    need(expected == ledger, 'P1_LEDGER_MISMATCH')
    return {**AUTH, 'test_count':count, 'budget':expected}

def prepare(folder, groups, inventory_path):
    folder = Path(folder)
    folder.mkdir()
    inv = current()
    def write(name, value):
        (folder / name).write_bytes(canonical(value))
    write('source-context.json', old.b.context.source_context())
    write('resources.json', resources.contract())
    write('protocol.json', _coverage(groups, inv, {}))
    write('preparation.json', _binding(folder, reference(inventory_path), inv))
    write('ledger.json', {})
    for _ in range(12):
        expected, ledger, count = _evaluate(folder, inv)
        if expected == ledger:
            return {**AUTH, 'test_count': count, 'budget': expected}
        write('ledger.json', expected)
    raise ValueError('P1_LEDGER_FIXED_POINT')

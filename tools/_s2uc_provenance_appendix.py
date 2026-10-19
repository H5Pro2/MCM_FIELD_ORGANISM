"""Neutral process -> immutable product -> separately committed provenance appendix.

Single writer, one same-directory staging file, no crash-recovery guarantee.
Observer result copies are immutable static evidence, not omitted from budgets.
The V9 child retains its existing job limit; the read-only appendix runs in the parent.
"""
import ast
import os
from pathlib import Path

from tools import _s2uc_provenance_inventory as previous
from tools import _s2uc_provenance_evaluation as evaluator
from tools import _s2uc_source_execution_binding as b
from tools import _s2uc_publication_v7 as publication
from tools import s2uc_source_process_once as process

VERSION = 's2uc.provenance-appendix.v1'
TEST = 'tests/test_s2uc_provenance_appendix.py'
ENTRIES = previous.ENTRIES + ('tools/_s2uc_provenance_appendix.py', TEST, 'tools/s2uc_appendix_check.py')
FILES = {'dependency-inventory.json': 'static_shared', 'provenance.json': 'verification',
         'appendix-terminal.json': 'terminal', 'appendix-error.json': 'error', 'appendix.tmp': 'staging'}
OBSERVER = {name: 'metadata' for name in ('config.json', 'bootstrap.json', 'parent-admission.json',
           'child-admission.json', 'after-imports.json', 'facts.json', 'stdout.txt')}
OBSERVER.update({'result.json': 'static_shared', 'process-exit.json': 'static_shared', 'stderr.txt': 'error'})
_write = publication._write
_replace = os.replace


def need(value, reason):
    if not value:
        raise ValueError(reason)


def current():
    inv = b.discovery._collect(b.discovery.ROOT, ENTRIES, 's2uc.appendix-inventory.v1')
    inv['external']['native_runtime'] = b.current()['external']['native_runtime']
    return inv


def test_ids():
    tree = ast.parse((b.discovery.ROOT / TEST).read_bytes())
    return sorted(previous.test_ids() + [f"{TEST[:-3].replace('/', '.')}.{c.name}.{m.name}"
                  for c in tree.body if isinstance(c, ast.ClassDef) for m in c.body
                  if isinstance(m, ast.FunctionDef) and m.name.startswith('test_')])


def _ref(data):
    return {'bytes': len(data), 'sha256': b.discovery.sha(data)}


def _read(root, name):
    return b.discovery.read_file(root, name)[1]


def _json(root, name):
    return b.old._json(_read(root, name))


def _snapshot(path, product, observer, appendix, inv, virtual=None):
    amounts = dict.fromkeys(b.resources.CATEGORIES, 0)
    files, identities = [], set()
    def add(space, root, name, category, expected=None):
        ref, _, identity = b.discovery.read_file(root, name)
        need(identity not in identities, 'APPENDIX_FILE_ALIAS')
        identities.add(identity)
        if expected is not None:
            need(all(ref[k] == expected[k] for k in ref), 'APPENDIX_CODE_CHANGED')
        amounts[category] += ref['bytes']
        if space != 'code':
            files.append({'space': space, **ref, 'category': category})
    for ref in inv['files']:
        add('code', b.discovery.ROOT, ref['path'], 'code', ref)
    need(amounts['code'] == inv['code_bytes'], 'APPENDIX_CODE_ACCOUNT_INVALID')
    for _, (space, name, category, _) in b.FILES.items():
        add(space, b.discovery.ROOT if space == 'project' else path.parent, name, category)
    add('bundle', path.parent, path.name, 'metadata')
    for space, root, mapping in (('product', product, b.old.RESULT_FILES), ('observer', observer, OBSERVER),
                                 ('appendix', appendix, FILES)):
        if not root.exists():
            need(space == 'product', 'APPENDIX_DIRECTORY_MISSING')
            continue
        need(root.is_dir() and not root.is_symlink() and not root.is_junction(), 'APPENDIX_DIRECTORY_INVALID')
        for p in sorted(root.iterdir()):
            need(p.name in mapping and p.is_file(), 'APPENDIX_UNREGISTERED_FILE')
            add(space, root, p.name, mapping[p.name])
    if virtual is not None:
        name, size = virtual
        need(not any(f['space'] == 'appendix' and f['path'] == name for f in files), 'APPENDIX_VIRTUAL_EXISTS')
        category = FILES[name]
        amounts[category] += size
        files.append({'space': 'appendix', 'path': name, 'bytes': size, 'category': category,
                      'sha256': None, 'self_reference': 'Own hash is held by the caller, never circularly embedded'})
    actual = b.resources.account('failure_after_publication', amounts)
    return {'files': files, 'actual': actual, 'code_inventory_sha256': b.discovery.sha(b.old.canonical(inv))}


def _pins(snapshot):
    return [r for r in snapshot['files'] if r['space'] != 'appendix']


def _observe(path, product, observer):
    cfg = _json(observer, 'config.json')
    exit = _json(observer, 'process-exit.json')
    need(exit['exit_code'] == 0 and exit['status'] == 'PRODUCT_RESULT_PRESENT', 'APPENDIX_PROCESS_NOT_CLOSED')
    result = _json(observer, 'result.json')
    need(result == exit['product'] and result['status'] == 'CLOSED_NEUTRAL_VERIFIED'
         and result['evaluation_allowed'] is True, 'APPENDIX_PRODUCT_NOT_VALID')
    binding = _json(path.parent, path.name)
    need(cfg['binding'] == str(path.resolve()) and cfg['output'] == product.resolve().as_posix()
         and cfg['run_id'] == binding['run_id'] and cfg['case'] == 'success'
         and cfg['folder'] == str(observer.resolve())
         and cfg['inventory_sha256'] == b.discovery.sha(_read(path.parent, 'dependency-inventory.json')),
         'APPENDIX_PROCESS_BINDING_INVALID')
    parent, child = (_json(observer, name + '-admission.json') for name in ('parent', 'child'))
    need(all(v['limit'] == 671088640 and v['flags'] == 0x2100 and v['member'] is True for v in (parent, child))
         and child['product_numpy_absent'] is True and child['ns'] < _json(observer, 'after-imports.json')['ns'],
         'APPENDIX_PROCESS_LIMIT_INVALID')
    need(_json(observer, 'facts.json') == {'calls': 58, 'gate': False, 'public_gate': False, 'real_production_calls': 0},
         'APPENDIX_SOURCE_FACTS_INVALID')
    for ref in result['result_inventory']:
        actual, _, _ = b.discovery.read_file(product, ref['path'])
        need(all(actual[k] == ref[k] for k in actual), 'APPENDIX_PRODUCT_BYTES_CHANGED')


def publish(binding_path, *, observer, directory):
    """Fresh separate appendix; errors never write to product or its binding."""
    path, observer, directory = Path(binding_path), Path(observer), Path(directory)
    # Path separation is checked before creating anything.
    product = Path(_json(path.parent, path.name)['output'])
    roots = [path.parent.resolve(), product.resolve(), observer.resolve(), directory.resolve()]
    need(all(not a.is_relative_to(c) and not c.is_relative_to(a) for i, a in enumerate(roots) for c in roots[i+1:]),
         'APPENDIX_ROOTS_MUST_BE_DISJOINT')
    directory.mkdir()  # Never overwrite an earlier appendix.
    inv = current()
    initial = _snapshot(path, product, observer, directory, inv)
    pins = _pins(initial)
    input_digest = b.discovery.sha(b.old.canonical(pins))
    reported = None
    try:
        reported = _json(product, 'terminal.json')['status']
    except Exception:
        pass
    valid = False
    stages = []
    def snapshot(virtual=None):
        return _snapshot(path, product, observer, directory, inv, virtual)
    def unchanged():
        need(_pins(snapshot()) == pins, 'APPENDIX_INPUTS_CHANGED')
    def atomic(name, data, guard=True):
        state = snapshot()
        if guard:
            unchanged()
        need(not (directory / name).exists() and not (directory / 'appendix.tmp').exists(), 'APPENDIX_TARGET_EXISTS')
        for category in ('staging', FILES[name]):
            sizes = dict(state['actual']['categories'])
            sizes[category] += len(data)
            measured = b.resources.account('failure_after_publication', sizes)
            need(measured['within_limits'], 'APPENDIX_BUDGET_EXCEEDED:' + ','.join(measured['violations']))
            stages.append({'file': name, 'placement': category, 'account': measured})
        _write(directory / 'appendix.tmp', data)
        need(_read(directory, 'appendix.tmp') == data, 'APPENDIX_STAGING_CHANGED')
        if guard:
            unchanged()
        _replace(directory / 'appendix.tmp', directory / name)
        need(_read(directory, name) == data, 'APPENDIX_PUBLISHED_CHANGED')
        if guard:
            unchanged()
    def receipt(status, reason, name):
        size = 0
        for _ in range(12):
            measured = snapshot((name, size))
            value = {'version': VERSION, 'appendix_status': status, 'product_status_reported': reported,
                     'product_validated_before_appendix': valid, 'reason': reason, 'input_snapshot_sha256': input_digest,
                     'evaluator_version': evaluator.VERSION, 'inventory': _ref(b.old.canonical(inv)),
                     'budget': measured, 'publication_steps': list(stages), 'real_execution_authorized': False}
            data = b.old.canonical(value)
            if len(data) == size:
                return data
            size = len(data)
        raise ValueError('APPENDIX_RECEIPT_SIZE_NOT_STABLE')
    try:
        need(initial['actual']['within_limits'], 'APPENDIX_INITIAL_BUDGET_EXCEEDED')
        _observe(path, product, observer)
        evaluation = evaluator.read_closed(path, product)
        need(evaluation['status'] == 'EVALUATED_NEUTRAL', 'APPENDIX_PRODUCT_NOT_EVALUABLE:' + evaluation.get('reason', ''))
        valid = True
        unchanged()
        report = {'version': VERSION, 'evaluator_version': evaluator.VERSION, 'inventory': _ref(b.old.canonical(inv)),
                  'input_snapshot_sha256': input_digest, 'evaluation': evaluation}
        atomic('dependency-inventory.json', b.old.canonical(inv))
        atomic('provenance.json', b.old.canonical(report))
        data = receipt('PUBLISHED', None, 'appendix-terminal.json')
        atomic('appendix-terminal.json', data)
        status, reason = 'PUBLISHED', None
    except Exception as exc:
        status, reason = 'NOT_PUBLISHED', str(exc) or type(exc).__name__
        stage = directory / 'appendix.tmp'
        cleanup = None
        if stage.exists():
            cleanup = snapshot()
            try:
                stage.unlink()
            except OSError:
                pass
        if cleanup is not None:
            stages.append({'failed_staging_observation': {
                'files': [r for r in cleanup['files'] if r['space'] == 'appendix' and r['category'] == 'staging'],
                'actual': cleanup['actual']}})
        try:
            atomic('appendix-error.json', receipt(status, reason, 'appendix-error.json'), guard=False)
        except Exception as failed:
            stages.append({'error_publication_failed': str(failed)})
    measured = snapshot()
    intact = _pins(measured) == pins
    accepted = status == 'PUBLISHED' and intact and measured['actual']['within_limits']
    return {'version': VERSION, 'product_status_reported': reported, 'product_validated_before_appendix': valid,
            'product_inputs_unchanged': intact, 'appendix_status': status if accepted or status != 'PUBLISHED' else 'NOT_PUBLISHED',
            'reason': reason, 'budget': measured, 'publication_steps': stages,
            'appendix_usable': accepted, 'real_execution_authorized': False}


def read_appendix(binding_path, *, observer, directory):
    """Revalidate bytes before consuming an appendix; never reevaluate provenance."""
    try:
        path, observer, directory = Path(binding_path), Path(observer), Path(directory)
        product = Path(_json(path.parent, path.name)['output'])
        need({p.name for p in directory.iterdir()} == {'dependency-inventory.json', 'provenance.json', 'appendix-terminal.json'},
             'APPENDIX_NOT_SUCCESS_ONLY')
        inv = current()
        need(_read(directory, 'dependency-inventory.json') == b.old.canonical(inv), 'APPENDIX_INVENTORY_CHANGED')
        state = _snapshot(path, product, observer, directory, inv)
        terminal = _json(directory, 'appendix-terminal.json')
        need(terminal['version'] == VERSION and terminal['appendix_status'] == 'PUBLISHED', 'APPENDIX_TERMINAL_INVALID')
        expected = terminal['budget']
        normalized = [dict(r) for r in state['files']]
        for row in normalized:
            if row['space'] == 'appendix' and row['path'] == 'appendix-terminal.json':
                row.update(sha256=None, self_reference='Own hash is held by the caller, never circularly embedded')
        need(sorted(normalized, key=lambda r:(r['space'],r['path'])) == sorted(expected['files'], key=lambda r:(r['space'],r['path']))
             and state['actual'] == expected['actual'] and state['actual']['within_limits'], 'APPENDIX_BYTES_OR_BUDGET_CHANGED')
        digest = b.discovery.sha(b.old.canonical(_pins(state)))
        report = _json(directory, 'provenance.json')
        need(terminal['input_snapshot_sha256'] == report['input_snapshot_sha256'] == digest
             and report['inventory'] == terminal['inventory'] == _ref(b.old.canonical(inv))
             and report['evaluator_version'] == terminal['evaluator_version'] == evaluator.VERSION
             and report['evaluation']['status'] == 'EVALUATED_NEUTRAL', 'APPENDIX_REPORT_BINDING_INVALID')
        _observe(path, product, observer)
        return {'appendix_status': 'VERIFIED', 'appendix_usable': True, 'budget': state, 'evaluation': report['evaluation']}
    except Exception as exc:
        return {'appendix_status': 'INVALID', 'appendix_usable': False, 'reason': str(exc) or type(exc).__name__}


def run_neutral(binding_path, *, observer, directory):
    """Explicit neutral orchestration; unchanged bounded V9 entry precedes appendix."""
    outcome = process.run_neutral(binding_path, folder=observer)
    result = publish(binding_path, observer=observer, directory=directory)
    return {'process_status': outcome['status'], 'process_exit_code': outcome['exit_code'], **result}

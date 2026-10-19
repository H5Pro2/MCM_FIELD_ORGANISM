"""Administrative entry: unchanged bound T1 worker, extra export accounting."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import s2uc_t1_prepare_v2 as p


if __name__ == '__main__':
    p.preparation_check()
    auth = ROOT / 'docs/S2UC_T1_V2_AUTORISIERUNG_20261003.json'
    template = p.q.old.read(p.TEMPLATE)
    expected = dict(template, status='AUTHORIZED_ONCE')
    p.q.validate_authorization(expected, p.authorization('AUTHORIZED_ONCE'))
    if auth.exists() or p.OUT.exists():
        raise RuntimeError('ONE_SHOT_ALREADY_CLAIMED')
    with auth.open('x', encoding='utf-8') as f:
        json.dump(expected, f, ensure_ascii=False, indent=2)
        f.write('\n')
    actual = p.q.old.read(auth)
    p.q.validate_authorization(actual, p.authorization('AUTHORIZED_ONCE'))
    dossier = ROOT / 'reports/s2uc/t1-preparation-assessment-20261003-01'
    seal = p.q.old.read(dossier / 'closure.json')
    for name, record in seal['files'].items():
        if p.q.old.sha(dossier / name) != record['sha256']:
            raise RuntimeError('DOSSIER_CHANGED')
    extra = sum(x.stat().st_size for x in dossier.iterdir() if x.is_file())
    base = p.charged_bytes(auth)
    # Reserve the complete external launch/assessment dossier in advance.
    report_reserve = 524288
    charged = base + extra + report_reserve
    if base + extra > 8 * 1048576:
        raise RuntimeError('PREPARATION_REFERENCE_CAP')
    record = dict(base_preparation_bytes=base, preparation_dossier_bytes=extra,
        external_report_reserved_bytes=report_reserve, charged_bytes=charged,
        authorization_sha256=p.q.old.sha(auth), binding_sha256=p.q.old.sha(p.BINDING),
        launcher_sha256=p.q.old.sha(__file__), authorization_only_status_changed=True,
        new_qualification=False, policy_changed=False)
    with Path(__file__).with_name('preflight.json').open('x', encoding='utf-8') as f:
        json.dump(record, f, indent=2)
        f.write('\n')
    print(json.dumps(record), flush=True)
    p.supervise(p.OUT, charged, p.worker,
        metadata=dict(authorization=actual, binding_sha256=p.q.old.sha(p.BINDING),
                      additional_accounting=record))

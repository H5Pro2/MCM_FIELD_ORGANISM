"""Seal recipes/code/runtime and write a PENDING template; never produce material."""
import ast
import json
import sys
from pathlib import Path
import numpy as np
from tools import s2uc_an_material as m


def save(path,value):
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def dependencies():
    pending=['tools/s2uc_an_material.py','tools/s2uc_an_compare.py','tools/s2uc_an_prepare.py',
             'tests/test_s2uc_an_material.py','tools/s2uc_an_qualify.py']
    found=set()
    while pending:
        name=pending.pop()
        if name in found:continue
        found.add(name)
        for node in ast.walk(ast.parse((m.ROOT/name).read_text(encoding='utf-8'))):
            modules=[]
            if isinstance(node,ast.Import):modules=[a.name for a in node.names]
            elif isinstance(node,ast.ImportFrom) and node.module:
                modules=[node.module]+[node.module+'.'+a.name for a in node.names]
            for module in modules:
                candidate=module.replace('.','/')+'.py'
                if module.startswith(('tools.','mcm_field_organism.','tests.')) and (m.ROOT/candidate).is_file():pending.append(candidate)
    return {name:m.sha(m.ROOT/name) for name in sorted(found)}


def seal():
    save(m.PLAN,m.plan())
    numpy_root=Path(np.__file__).parent
    numpy_files={str(f.relative_to(numpy_root)).replace('\\','/'):m.sha(f)
        for f in sorted(numpy_root.rglob('*')) if f.suffix in ('.py','.pyd','.dll')}
    binding=dict(version='s2uc.an.production-binding.v1',status='BOUND_NOT_AUTHORIZED',
        plan_path=str(m.PLAN.relative_to(m.ROOT)).replace('\\','/'),plan_sha256=m.sha(m.PLAN),
        contract_sha256=m.sha(m.ROOT/m.CONTRACT),code=dependencies(),python=sys.version,
        python_executable_sha256=m.sha(sys.executable),numpy_version=np.__version__,numpy_files=numpy_files)
    save(m.BINDING,binding)
    save(m.ROOT/'docs/S2UC_AN_DEV_AUTORISIERUNG_VORLAGE_20261001.json',
        dict(status='PENDING',action='PRODUCE_AN_PARTITION',partition='AN-DEV',
            binding_sha256=m.sha(m.BINDING),plan_sha256=m.sha(m.PLAN),python=sys.version))
    return dict(plan_sha256=m.sha(m.PLAN),binding_sha256=m.sha(m.BINDING),bound_code_files=len(binding['code']))


if __name__=='__main__':print(json.dumps(seal(),indent=2))

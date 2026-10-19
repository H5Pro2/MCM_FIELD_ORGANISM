from types import MappingProxyType
from tools import _s2uc_resources_v9 as old

VERSION = 's2uc.preparation-resources.p1'
LIMITS = MappingProxyType({**old.LIMITS, 'code': 868340})
RESERVES = old.RESERVES

def account(amounts):
    result = old.account('failure_before_publication', amounts)
    violations = [v for v in result['violations'] if v != 'limit:code']
    if amounts['code'] > LIMITS['code']:
        violations.append('limit:code')
    return {**result, 'violations': violations, 'within_limits': not violations}

def contract():
    return {'version': VERSION, 'limits': dict(LIMITS), 'reserves': dict(RESERVES),
            'scope': 'PREPARATION_ONLY', 'real_execution_authorized': False,
            'protocol_limit': 32768, 'inventory_limit': 16384}

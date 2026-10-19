"""Compact FW1 receipts require all four arms and independent condition verification."""
def condition_receipt(pair,label,r):
    if not r['complete'] or not r['cleanup'] or not r['stock_equal'] or r['integrity']!='PASS_DELTA_INTEGRITY':raise ValueError('CONDITION_INCOMPLETE')
    return {k:r[k] for k in ('complete','cleanup','stock_equal','integrity','targets','KEEP','RESET','resets')}|dict(pair=pair,condition=label)
def pair_receipt(pair,conditions):
    if set(conditions)!={'A','B'}:raise ValueError('PAIR_INCOMPLETE')
    for label,c in conditions.items():
        if c['pair']!=pair or c['condition']!=label or not all(c[k] for k in ('complete','cleanup','stock_equal')) or c['integrity']!='PASS_DELTA_INTEGRITY':raise ValueError('PAIR_BINDING')
    if conditions['A']['targets']!=conditions['B']['targets']:raise ValueError('PAIR_TARGETS')
    return dict(pair=pair,orientation=(pair-1)%2,complete=True,conditions=conditions)

"""Strict structural comparison; only observation_end generation keys normalize."""
import math,re,struct
MAX_GENERATION=(1<<64)-1

def generation_key(key):
    if type(key) is int:
        value=key
    elif type(key) is str and re.fullmatch(r'[1-9][0-9]{0,19}',key,flags=re.ASCII):
        value=int(key)
    else:raise ValueError('GENERATION_KEY_INVALID')
    if not 1<=value<=MAX_GENERATION:raise ValueError('GENERATION_KEY_RANGE')
    return value

def generation_map(value):
    if type(value) is not dict:raise ValueError('GENERATION_MAP_INVALID')
    result={}
    for key,end in value.items():
        normalized=generation_key(key)
        if normalized in result:raise ValueError('GENERATION_KEY_COLLISION')
        result[normalized]=end
    return result

def _tree(value,*,marks=False):
    if marks:value=generation_map(value)
    if type(value) is dict:
        entries=[]
        for key,item in value.items():
            if type(key) not in (str,int):raise ValueError('STRUCTURAL_KEY_INVALID')
            entries.append(((type(key).__name__,key),_tree(item,marks=key=='observation_end')))
        return ('object',frozenset(entries))
    if type(value) in (tuple,list):return ('array',tuple(_tree(v) for v in value))
    if type(value) is float:
        if not math.isfinite(value):raise ValueError('STRUCTURAL_NONFINITE')
        return ('float',struct.pack('>d',value))
    if value is None or type(value) in (bool,int,str):return (type(value).__name__,value)
    raise ValueError('STRUCTURAL_VALUE_INVALID')

def structured_equal(left,right):
    # Mapping insertion order is irrelevant; arrays retain their exact order.
    # JSON arrays are represented as lists or tuples on either side.
    return _tree(left)==_tree(right)

def stock_equal(left,right):
    if type(left) is not dict or type(right) is not dict:raise ValueError('STOCK_INVALID')
    if 'observation_end' not in left or 'observation_end' not in right:raise ValueError('ENDMARKS_MISSING')
    return structured_equal(left,right)

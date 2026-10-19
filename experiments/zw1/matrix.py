"""Fixed recipe; no seed argument, no outcome input."""
import hashlib

def generate():
    return bytes(2*(int.from_bytes(hashlib.sha256(f'MCM-ZW1/bootstrap/v1/row={r}/column={c}'.encode()).digest()[:8],'big')%8)+c//8 for r in range(10000) for c in range(16))

def verify(data):
    if len(data)!=160000:raise ValueError('MATRIX_SIZE')
    for position,value in enumerate(data):
        row,column=divmod(position,16)
        digest=hashlib.sha256(('MCM-ZW1/bootstrap/v1/row=%d/column=%d'%(row,column)).encode()).hexdigest()
        expected=(int(digest[14:16],16)&7)*2+int(column>=8)
        if value!=expected:raise ValueError('MATRIX_REFERENCE:'+str(position))
    return hashlib.sha256(data).hexdigest()

def shape(data):
    if len(data)!=160000 or any(x>=16 or x%2!=(i%16)//8 for i,x in enumerate(data)):raise ValueError('MATRIX_PAIR_STRATA')

import sys, hashlib
sys.path.insert(0,"tools"); sys.path.insert(0,"experiments/nrbf_writeback")
import pkp_dump as pd
p="samples/DSC_12G-HD/pkp/extr_17_17677_v1_0_0.pkp"
P=pd.PkpParser(pd.load_bytes(p)); P.parse()
objs=P.objects
def dr(x):
    seen=0
    while isinstance(x,dict) and set(x)=={'ref'} and seen<20:
        x=objs.get(x['ref']); seen+=1
    if isinstance(x,dict) and 'ref' in x and len(x)==1: x=objs.get(x['ref'])
    return x
root=objs[P.root_id]
print("ROOT class:", root.get('class') or root.get('name'))
print("ROOT members:", list((root.get('members') or {}).keys()))

import sys
sys.path.insert(0,"tools"); sys.path.insert(0,"experiments/nrbf_writeback")
import pkp_dump as pd
p="samples/DSC_12G-HD/pkp/extr_17_17677_v1_0_0.pkp"
P=pd.PkpParser(pd.load_bytes(p)); P.parse(); objs=P.objects
def D(x,n=0):
    while isinstance(x,dict) and '$ref' in x and len(x)==1 and n<40: x=objs.get(x['$ref']); n+=1
    return x
def name(o):
    if not isinstance(o,dict): return None
    return D((o.get('members') or {}).get('AssetBase+_name')) or D((o.get('members') or {}).get('_name'))
def kids(o):
    for k in (o.get('members') or {}):
        if k.endswith('_internalChildCollection'):
            cc=D((o['members'])[k])
            if isinstance(cc,dict):
                for mk in ('items','_items'):
                    if mk in cc: return [D(i) for i in cc[mk] if D(i) is not None]
                m=cc.get('members') or {}
                for mk,mv in m.items():
                    v=D(mv)
                    if isinstance(v,dict) and 'items' in v: return [D(i) for i in v['items'] if D(i) is not None]
    return []
root=objs[P.root_id]
def walk(o,depth=0,maxd=3):
    for c in kids(o):
        print("  "*depth, "-", c.get('class'), "name=",repr(name(c)))
        if depth<maxd: walk(c,depth+1,maxd)
print("ROOT", root.get('class'), "name=",repr(name(root)))
walk(root,1,2)

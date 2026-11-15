import sys
sys.path.insert(0,"tools"); sys.path.insert(0,"experiments/nrbf_writeback")
import pkp_dump as pd
p="samples/DSC_12G-HD/pkp/extr_17_17677_v1_0_0.pkp"
P=pd.PkpParser(pd.load_bytes(p)); P.parse(); objs=P.objects
def D(x,n=0):
    while isinstance(x,dict) and '$ref' in x and len(x)==1 and n<40: x=objs.get(x['$ref']); n+=1
    return x
def nm(o):
    m=o.get('members') or {}
    for k in m:
        if k.endswith('_name'): 
            v=D(m[k])
            if isinstance(v,str): return v
    return None
def childitems(o):
    m=o.get('members') or {}
    out=[]
    for k,v in m.items():
        if k.endswith('_internalChildCollection'):
            cc=D(v)
            if not isinstance(cc,dict): continue
            lst=D((cc.get('members') or {}).get('Collection`1+items'))
            if isinstance(lst,dict):
                arr=D((lst.get('members') or {}).get('_items'))
                size=D((lst.get('members') or {}).get('_size')) or 0
                if isinstance(arr,dict) and 'items' in arr:
                    for it in arr['items'][:size]:
                        d=D(it)
                        if isinstance(d,dict): out.append(d)
            break
    return out
def walk(o,depth=0,maxd=2):
    for c in childitems(o):
        print("   "*depth+"- %-70s name=%r" % (c.get('class'), nm(c)))
        if depth<maxd: walk(c,depth+1,maxd)
root=objs[P.root_id]
print("ROOT %s name=%r"%(root.get('class'),nm(root)))
walk(root,1,2)

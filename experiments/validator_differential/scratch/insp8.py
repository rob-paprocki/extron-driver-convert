import sys,json
sys.path.insert(0,"tools"); sys.path.insert(0,"experiments/nrbf_writeback")
import pkp_dump as pd
p="samples/DSC_12G-HD/pkp/extr_17_17677_v1_0_0.pkp"
P=pd.PkpParser(pd.load_bytes(p)); P.parse(); objs=P.objects
def D(x,n=0):
    while isinstance(x,dict) and '$ref' in x and len(x)==1 and n<40: x=objs.get(x['$ref']); n+=1
    return x
o=objs[7]
print("oid7:", o.get('class'), list((o.get('members') or {}).keys()))
for k,v in (o.get('members') or {}).items():
    dv=D(v)
    print("  ",k,"->", (dv.get('class') if isinstance(dv,dict) else repr(dv)))
    if isinstance(dv,dict) and 'items' in dv: print("      items:", dv['items'][:10], "n=",len(dv['items']))
    if isinstance(dv,dict) and 'members' in dv:
        for k2,v2 in dv['members'].items():
            d2=D(v2)
            print("      ",k2,"->",(d2.get('class') if isinstance(d2,dict) else repr(d2)))
            if isinstance(d2,dict) and 'items' in d2:
                print("          items n=%d:"%len(d2['items']), d2['items'][:12])

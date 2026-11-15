import sys, hashlib
sys.path.insert(0,"tools"); sys.path.insert(0,"experiments/nrbf_writeback")
import pkp_dump as pd
def dump(p):
    print("="*70); print(p)
    P=pd.PkpParser(pd.load_bytes(p)); P.parse(); objs=P.objects
    def dr(x, n=0):
        while isinstance(x,dict) and '$ref' in x and len(x)==1 and n<30:
            x=objs.get(x['$ref']); n+=1
        return x
    root=objs[P.root_id]; M=root['members']
    print("filename:", dr(M.get('DriverDescriptorAsset+_filename')))
    man=dr(M['_manifest'])
    print("manifest class:", man.get('class'))
    print("manifest members:", list((man.get('members') or {}).keys()))
    # find child collection
    for mk,mv in (man.get('members') or {}).items():
        if 'ChildCollection' in mk or 'child' in mk.lower():
            cc=dr(mv)
            print("  ",mk,"->",type(cc), cc.get('class') if isinstance(cc,dict) else '')
            if isinstance(cc,dict):
                print("     members:",list((cc.get('members') or {}).keys()) if 'members' in cc else 'items:%d'%len(cc.get('items') or []))
    # brute: walk everything for ResourceAsset objects
    res=[]
    for oid,o in objs.items():
        if isinstance(o,dict) and isinstance(o.get('class'),str) and 'ResourceAsset' in o['class']:
            res.append((oid,o))
    print("ResourceAsset-ish objects: %d"%len(res))
    for oid,o in res:
        mm=o.get('members') or {}
        key=dr(mm.get('_key'))
        content=dr(mm.get('_content'))
        ct=dr(mm.get('_contentType'))
        g=dr(mm.get('AssetBase+_guid'))
        nm=dr(mm.get('AssetBase+_name'))
        clen=None; kind=type(content).__name__
        if isinstance(content,str): clen=len(content); sha=hashlib.sha256(content.encode('utf-8')).hexdigest()
        elif isinstance(content,dict) and 'items' in content:
            b=bytes(content['items']); clen=len(b); sha=hashlib.sha256(b).hexdigest(); kind='bytes'
        else: sha=None
        print("  oid=%s class=%s key=%r name=%r contentkind=%s len=%s sha=%s" % (oid,o['class'],key,nm,kind,clen,(sha or '')[:16]))
    # hash dict
    d=dr(root['members']['_resourceHashDict'])
    kv=dr((d.get('members') or {}).get('KeyValuePairs'))
    print("hashdict entries:")
    for it in (kv or {}).get('items') or []:
        e=dr(it)
        if not isinstance(e,dict): continue
        mm=e.get('members') or {}
        k=dr(mm.get('key')); v=dr(mm.get('value'))
        vb=bytes(v['items']) if isinstance(v,dict) and 'items' in v else None
        print("   key=%r digest=%s" % (k, vb.hex() if vb else None))
for p in ["samples/DSC_12G-HD/pkp/extr_17_17677_v1_0_0.pkp","samples/Tesira/pkp/biam_25_150_v1_20_0.pkp"]:
    dump(p)

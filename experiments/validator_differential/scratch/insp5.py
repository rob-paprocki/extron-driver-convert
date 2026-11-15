import sys, hashlib
sys.path.insert(0,"tools"); sys.path.insert(0,"experiments/nrbf_writeback")
import pkp_dump as pd
def D(objs,x,n=0):
    while isinstance(x,dict) and '$ref' in x and len(x)==1 and n<40:
        x=objs.get(x['$ref']); n+=1
    return x
for p in ["samples/DSC_12G-HD/pkp/extr_17_17677_v1_0_0.pkp","samples/Tesira/pkp/biam_25_150_v1_20_0.pkp","samples/Samsung QNxxLS03DAFXZA/pkp/smsg_10_6738_v1_0_0.pkp"]:
    P=pd.PkpParser(pd.load_bytes(p)); P.parse(); objs=P.objects
    print("="*70); print(p)
    root=objs[P.root_id]
    print(" filename:", D(objs,root['members'].get('DriverDescriptorAsset+_filename')))
    for oid,o in objs.items():
        if isinstance(o,dict) and o.get('class','').endswith('StreamResourceAsset'):
            mm=o['members']
            print("  RES oid=%d members=%s"%(oid,list(mm.keys())))
            key=D(objs,mm.get('_key')); name=D(objs,mm.get('AssetBase+_name')); g=D(objs,mm.get('AssetBase+_guid'))
            cont=D(objs,mm.get('_content'))
            if isinstance(cont,dict) and 'items' in cont:
                b=bytes(cont['items']); info="bytes len=%d sha256=%s"%(len(b),hashlib.sha256(b).hexdigest())
            elif isinstance(cont,str):
                b=cont.encode('utf-8'); info="str len=%d sha256=%s"%(len(b),hashlib.sha256(b).hexdigest())
            else: info="content=%r"%(cont if not isinstance(cont,dict) else list(cont.keys()))
            print("     key=%r name=%r guid=%r"%(key,name,g))
            print("     ",info)
    d=D(objs,root['members']['_resourceHashDict'])
    kv=D(objs,(d.get('members') or {}).get('KeyValuePairs'))
    for it in (kv or {}).get('items') or []:
        e=D(objs,it)
        if not isinstance(e,dict): continue
        k=D(objs,e['members'].get('key')); v=D(objs,e['members'].get('value'))
        print("  HASH key=%r digest=%s"%(k, bytes(v['items']).hex() if isinstance(v,dict) and 'items' in v else v))

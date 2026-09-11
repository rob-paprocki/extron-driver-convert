import sys, hashlib
sys.path.insert(0,"tools"); sys.path.insert(0,"experiments/nrbf_writeback")
import pkp_dump as pd
def D(objs,x,n=0):
    while isinstance(x,dict) and '$ref' in x and len(x)==1 and n<40:
        x=objs.get(x['$ref']); n+=1
    return x
def guid_str(g):
    if not isinstance(g,dict): return g
    m=g['members']
    return "%08x-%04x-%04x-%02x%02x-%02x%02x%02x%02x%02x%02x"%(m['_a']&0xffffffff,m['_b']&0xffff,m['_c']&0xffff,m['_d']&0xff,m['_e']&0xff,m['_f']&0xff,m['_g']&0xff,m['_h']&0xff,m['_i']&0xff,m['_j']&0xff,m['_k']&0xff)
for p in ["samples/DSC_12G-HD/pkp/extr_17_17677_v1_0_0.pkp","samples/Samsung QNxxLS03DAFXZA/pkp/smsg_10_6738_v1_0_0.pkp"]:
    P=pd.PkpParser(pd.load_bytes(p)); P.parse(); objs=P.objects
    print("="*70); print(p)
    for oid,o in objs.items():
        if isinstance(o,dict) and o.get('class','').endswith('StreamResourceAsset'):
            mm=o['members']
            key=D(objs,mm.get('ResourceAssetBase+_key'))
            name=D(objs,mm.get('AssetBase+_name'))
            g=D(objs,mm.get('AssetBase+_guid'))
            cont=D(objs,mm.get('ResourceAssetBase+_content'))
            if isinstance(cont,dict) and 'items' in cont:
                b=bytes(cont['items']); info="BYTES len=%d sha256=%s"%(len(b),hashlib.sha256(b).hexdigest())
                info+="  head=%r"%b[:16]
            elif isinstance(cont,str):
                b=cont.encode('utf-8'); info="STR len=%d sha256(utf8)=%s"%(len(b),hashlib.sha256(b).hexdigest())
            else:
                info="content=%s"%(type(cont).__name__ if not isinstance(cont,dict) else "dict:"+str(list(cont.keys()))+" class="+str(cont.get('class')))
            print("  oid=%d key=%r name=%r guid=%s"%(oid,key,name,guid_str(g)))
            print("      "+info)

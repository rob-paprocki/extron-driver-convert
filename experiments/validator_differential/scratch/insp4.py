import sys, hashlib, json
sys.path.insert(0,"tools"); sys.path.insert(0,"experiments/nrbf_writeback")
import pkp_dump as pd
p="samples/DSC_12G-HD/pkp/extr_17_17677_v1_0_0.pkp"
P=pd.PkpParser(pd.load_bytes(p)); P.parse(); objs=P.objects
root=objs[P.root_id]; M=root['members']
print("raw _manifest:", repr(M.get('_manifest')))
print("raw _internalChildCollection:", repr(M.get('_internalChildCollection')))
print("raw AssetBase+_internalChildCollection:", repr(M.get('AssetBase+_internalChildCollection')))
print("raw DriverDescriptorAsset+_internalChildCollection:", repr(M.get('DriverDescriptorAsset+_internalChildCollection')))
# class census
from collections import Counter
c=Counter()
for oid,o in objs.items():
    if isinstance(o,dict) and isinstance(o.get('class'),str): c[o['class']]+=1
for k,v in c.most_common(40): print("%5d  %s"%(v,k))

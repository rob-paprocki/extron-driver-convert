import sys, os, json
sys.path.insert(0,"tools"); sys.path.insert(0,"experiments/nrbf_writeback")
import pkp_dump as pd
p="samples/DSC_12G-HD/pkp/extr_17_17677_v1_0_0.pkp"
P=pd.PkpParser(pd.load_bytes(p)); P.parse() if hasattr(P,'parse') else None
print([m for m in dir(P) if not m.startswith('_')][:40])

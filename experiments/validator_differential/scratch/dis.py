il=bytes.fromhex("033ab800000038a80000003886000000027b23000004076ff400000a6ffb00000a08281b00002b2d6d2b5b066ff600000a0b076f9900000a0c036ffd00000a076f8500000a6f9700000a2c252b00036ffd00000a076f8500000a6ffe00000a08281b00002b2d2f2b0020d53801000dde77027b23000004076ff400000a6ff700000a2c0a2b8a20d53801000dde5a20d63801000dde52066f6000000a3a8affffff2b00de41062c0a2b00066f2e00000a2b00dc725c06007073ff00000a7a036f8600000a729c060070196f0001000a2c042b00162a036f8b00000a6ff300000a0a3825ffffff162a092a")
import struct
one={0x00:'nop',0x02:'ldarg.0',0x03:'ldarg.1',0x06:'ldloc.0',0x07:'ldloc.1',0x08:'ldloc.2',0x09:'ldloc.3',
0x0A:'stloc.0',0x0B:'stloc.1',0x0C:'stloc.2',0x0D:'stloc.3',0x14:'ldnull',0x16:'ldc.i4.0',0x19:'ldc.i4.3',
0x25:'dup',0x26:'pop',0x2A:'ret',0x7A:'throw',0xDC:'endfinally'}
tok4={0x28:'call',0x6F:'callvirt',0x72:'ldstr',0x73:'newobj',0x7B:'ldfld',0x20:'ldc.i4'}
br4={0x38:'br',0x39:'brfalse',0x3A:'brtrue'}
br1={0x2B:'br.s',0x2C:'brfalse.s',0x2D:'brtrue.s',0xDE:'leave.s'}
i=0
while i<len(il):
    o=il[i]; s="%04X: "%i
    if o in one: print(s+one[o]); i+=1
    elif o in tok4:
        v=struct.unpack_from('<I',il,i+1)[0]; print(s+"%s 0x%08X"%(tok4[o],v)); i+=5
    elif o in br4:
        d=struct.unpack_from('<i',il,i+1)[0]; print(s+"%s -> %04X"%(br4[o],i+5+d)); i+=5
    elif o in br1:
        d=struct.unpack_from('<b',il,i+1)[0]; print(s+"%s -> %04X"%(br1[o],i+2+d)); i+=2
    else: print(s+"?? %02x"%o); i+=1

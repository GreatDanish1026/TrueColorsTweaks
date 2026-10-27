import struct,os,sys,zlib,fnmatch
path,cmd,pat=sys.argv[1],sys.argv[2],sys.argv[3]
out=sys.argv[4] if len(sys.argv)>4 else None
f=open(path,'rb'); sz=os.path.getsize(path); f.seek(sz-300); t=f.read()
i=t.rfind(struct.pack('<I',0x5A6F12E1))
ver,ioff,isz=struct.unpack_from('<IQQ',t,i+4)
comp=t[i+4+20+20+1:]
names=[comp[k*32:(k+1)*32].rstrip(b'\0').decode() for k in range(len(comp)//32)]
f.seek(ioff); b=f.read(isz); o=0
def i32():
    global o; v=struct.unpack_from('<i',b,o)[0]; o+=4; return v
def fs():
    global o; n=i32()
    if n<0: s=b[o:o-n*2].decode('utf-16le')[:-1]; o+=-n*2
    else: s=b[o:o+n][:-1].decode('latin-1'); o+=n
    return s
mount=fs(); n=i32()
for _ in range(n):
    name=fs()
    off,size,usize,cm=struct.unpack_from('<QQQI',b,o); o+=28+20
    blocks=[]
    if cm:
        nb=i32(); blocks=[struct.unpack_from('<QQ',b,o+16*k) for k in range(nb)]; o+=16*nb
    enc=b[o]; o+=1; bs=struct.unpack_from('<I',b,o)[0]; o+=4
    if not fnmatch.fnmatch(name.lower(),pat.lower()): continue
    if cmd=='list': print(usize,name,'enc' if enc else '',names[cm-1] if cm else '')
    else:
        data=b''
        if cm:
            for s_,e_ in blocks:
                f.seek(off+s_); data+=zlib.decompress(f.read(e_-s_))
        else:
            f.seek(off); hdr=f.read(53+8); f.seek(off+53); data=f.read(size)
        p=os.path.join(out,name.replace('/',os.sep)); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'wb').write(data); print('wrote',p,len(data))

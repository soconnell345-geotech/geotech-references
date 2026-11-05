"""Page-text helpers for scripts/build_gec12_appendix_d.py (GEC-12 Vol III Appendix D)."""
import re, json, sys
import pymupdf as fitz
from pathlib import Path
PDF=str(Path(__file__).resolve().parents[1]/"docs"/"GEC 12 Vol 3.pdf")
doc=fitz.open(PDF)
OFF=34
MATH=re.compile(r'[\U0001D400-\U0001D7FF∑∫√≤≥∙ቀቁ]')
def page_lines(i):
    t=doc[i].get_text()
    L=[l.rstrip() for l in t.split("\n")]
    L=[l for l in L if l.strip()]
    if L and re.fullmatch(r'\s*\d{1,3}\s*',L[-1]): L=L[:-1]
    return L
def heads(first,last):
    H=[]
    for l,t,p in doc.get_toc():
        m=re.match(r'(D\.\d+(?:\.\d+)*)\s+(.*)',t.strip())
        if m and first<=p<=last: H.append((m.group(1),re.sub(r'\s+',' ',m.group(2)).strip(),p))
    return H
def extract(first,last):
    """first,last: 1-based PDF pages. returns list of (page, line)"""
    out=[]
    for i in range(first-1,last):
        for l in page_lines(i): out.append((i+1,l))
    return out
def build(first,last,extra_heads=()):
    H=heads(first,last)+list(extra_heads)
    lines=extract(first,last)
    # locate heading starts
    idx=[]
    for sid,title,p in H:
        key=(sid+" "+title)[:25].replace(" ","")
        found=None
        for k,(pg,l) in enumerate(lines):
            if pg in (p,p+1) and l.replace(" ","").startswith(key[:max(8,len(sid)+6)]):
                found=k;break
        if found is None: print("HEAD NOT FOUND",sid,title,p,file=sys.stderr); continue
        idx.append((found,sid,title,p))
    idx.sort()
    secs=[]
    for n,(k,sid,title,p) in enumerate(idx):
        end=idx[n+1][0] if n+1<len(idx) else len(lines)
        # skip heading line(s): title may wrap
        body=lines[k+1:end]
        full=(sid+" "+title).replace(" ","")
        acc=lines[k][1].replace(" ","")
        while body and len(acc)<len(full) and full.startswith(acc+body[0][1].replace(" ","")[:3]) :
            acc+=body[0][1].replace(" ",""); body=body[1:]
        secs.append(dict(sid=sid,title=title,page=p,lines=body))
    return secs
import unicodedata
CAPS={}
for _l,_t,_p in doc.get_toc():
    _m=re.match(r'(Figure|Table)\s+(D-\d+)\s+(.*)',_t.strip())
    if _m: CAPS.setdefault((_m.group(1),_m.group(2)),re.sub(r'\s+',' ',_m.group(3)).strip())
def demath(s):
    out=[];i=0
    while i<len(s):
        if MATH.search(s[i]) and '\U0001D400'<=s[i]<='\U0001D7FF':
            j=i
            while j<len(s) and '\U0001D400'<=s[j]<='\U0001D7FF': j+=1
            run=s[i:j]
            if len(run)%2==0 and all(run[k]==run[k+1] for k in range(0,len(run),2)): run=run[::2]
            out.append(unicodedata.normalize('NFKC',run)); i=j
        else:
            out.append(s[i]); i+=1
    return "".join(out)
def is_display(s):
    m=sum(1 for c in s if '\U0001D400'<=c<='\U0001D7FF' or c in '∑∫√ቀቁ')
    words=re.findall(r'[A-Za-z]{4,}',s)
    return m>0 and (len(words)<3 or m>len(s)*0.4)
def render(sec):
    out=[]; figs=[]; tabs=[]; eqs=[]
    lastpg=None; L=sec['lines']; i=0
    while i<len(L):
        pg,l=L[i]
        if pg!=lastpg:
            out.append(f"[p. {pg-OFF}]"); lastpg=pg
        s=l.strip()
        m=re.match(r'(Figure|Table)\s+(D-\d+)\b\s*(.*)$',s)
        if m and (m.group(1),m.group(2)) in CAPS and (not m.group(3) or CAPS[(m.group(1),m.group(2))].replace(' ','').startswith(demath(m.group(3)).replace(' ','')[:15])):
            full=CAPS[(m.group(1),m.group(2))]; key=full.replace(' ','')
            acc=demath(m.group(3)).replace(' ',''); j=i+1
            while j<len(L) and len(acc)<len(key) and key.startswith((acc+demath(L[j][1]).replace(' ',''))[:len(key)][:max(len(acc)+3,1)]):
                acc+=demath(L[j][1]).replace(' ',''); j+=1
            capt=full
            if m.group(1)=='Figure':
                figs.append((m.group(2),capt,pg-OFF)); i=j; continue
            # table: gather short cell lines
            cells=[]
            while j<len(L) and (len(L[j][1].strip())<48 and not re.match(r'(Figure|Table)\s+D-\d+',L[j][1].strip())):
                cells.append(L[j][1].strip()); j+=1
            tabs.append(dict(table_id=m.group(2),title=capt,cells=cells,page=pg-OFF))
            out.append(f"[Table {m.group(2)}]"); i=j; continue
        mt=re.fullmatch(r'\[?Eq\.\s*([\dD]+-\d+)\]?',s)
        if mt:
            out.append(f"[Eq. {mt.group(1)}]"); eqs.append(mt.group(1)); i+=1; continue
        if is_display(s):
            if not out or out[-1]!="[equation shown on the page]": out.append("[equation shown on the page]")
            i+=1; continue
        s=demath(s)
        mm=re.fullmatch(r'\[Eq\.\s*([\dD]+-\d+)\]',s)
        if mm:
            out.append(f"[Eq. {mm.group(1)}]"); eqs.append(mm.group(1)); i+=1; continue
        out.append(s); i+=1
    txt=" ".join(out)
    txt=re.sub(r'\s+',' ',txt).strip()
    return txt,figs,tabs,eqs

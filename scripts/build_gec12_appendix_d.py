"""Build GEC-12 Volume III Appendix D (Comprehensive Design Examples) text
from the printed pages (no API), as geotech_references/gec_12/text/appendix_d.json.

BACKLOG REF-52. Sections are the PDF outline's D.x headings (every printed
heading is in it); each body is the print's own wording between headings,
with a [p. N] mark where each printed page starts (printed page = PDF page
- 34). A display equation, whose glyphs the text layer maps wrongly, is left
as "[equation shown on the page]" next to its printed tag ([Eq. 7-61]); the
appendix's own Eqs. D-1 to D-7 are typed in below from the rendered pages.
Math-italic symbols inside sentences are read by halving their doubled
glyphs, and the subscripts the text layer maps wrongly (Rndr, φdyn, σdr ...)
are corrected from the renders (FIX). Each table's cells are kept as printed,
read across each row; Tables D-6, D-51 and D-100 are given row by row.
Sections over the reference tools' size are split into lettered parts (the
letters are not printed), as scripts/build_printed_text.py does.

Usage: python scripts/build_gec12_appendix_d.py geotech_references/gec_12/text/appendix_d.json
"""
import sys, re, json
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent))
import gec12_appendix_d_extract as g12x
OFF=34
secs=g12x.build(35,299)
# intro section "D" (p. 1): text before D.1 on PDF 35
intro_lines=[(35,l) for l in g12x.page_lines(34)]
FIX=[("WBBBBB","WBlock"),("Ruu","Rug"),("Mrr","Mrx"),("Vuu","Vuy"),("σ′vv","σ′vo"),("Muu","Mux"),("Rnnn","Rndr"),("Qmmm","Qmax"),("Dmmm−ttttttt","Dmin−tension"),("γ′ssss","γ′soil"),("D(iiiiiiiiii)","D(individual)"),("φssss","φstat"),("φddd","φdyn"),("σdd","σdr"),(",φ-dyn.=","φdyn="),(",φ-stat.=","φstat="),(", ,φ-","φ"),("bridges will be approximately 200 feet long with a higher approach embankment required on the south side.5.","bridges will be approximately 200 feet long with a higher approach embankment required on the south side. 5.")]
def fix(t):
    t=g12x.demath(t) if any('\U0001D400'<=c<='\U0001D7FF' for c in t) else t
    for a,b in FIX: t=t.replace(a,b)
    t=re.sub(r'φ-(dyn|stat|c\(min\))\.',r'φ\1',t); t=t.replace(",φ","φ")
    return t
EQM="[equation shown on the page]"
def clean_eq(t):
    for ch in "ቃ൬ℎ": t=t.replace(ch,"")
    frag=r'(?:[^\[\]A-Za-z]|\b[A-Za-z]{1,3}\b)'
    for _ in range(4):
        t=re.sub(r'\[equation shown on the page\]\s*'+frag+r'{0,40}?\s*(?=\[(?:equation shown|Eq\.|p\. ))',EQM+' ',t)
        t=re.sub(r'(?<=[.:)]) '+frag+r'{1,25}?\s*(?=\[equation shown)',' ',t)
        t=re.sub(r'(\[equation shown on the page\]\s*)+',EQM+' ',t)
    return re.sub(r'\s+',' ',t)
def collapse_pages(t):
    t=clean_eq(t)
    t=re.sub(r'(\[p\. \d+\]\s*)+(?=\[p\. \d+\])','',t)        # runs of markers -> last
    t=re.sub(r'\s*\[p\. \d+\]\s*$','',t)
    return t.strip()
EQS={
 "D-1":("Volume of an inverted obelisk soil block layer (group uplift soil block)","V = (h/6) [Zbottom Btop + Ztop Bbottom + 2 * (Ztop Btop + Zbottom Bbottom)]",{"V":"volume of the block layer","h":"layer height (thickness)","Ztop, Zbottom":"block length at the top and bottom of the layer","Btop, Bbottom":"block width at the top and bottom of the layer"}),
 "D-2":("Vertical stress increase under a strip load (embankment surcharge treated as a strip load, Figure D-30)","Δσv = (q/Π) [β + sin(β) * cos(β + 2δ)]",{"q":"strip (embankment) surcharge pressure","β, δ":"angles by Eq. D-3 and Eq. D-4 (Figure D-30)"}),
 "D-3":("Angle β for the strip load stress increase","β = tan^-1((x+b)/z) − tan^-1((x−b)/z)",{"x":"horizontal distance (Figure D-30)","b":"half width of the strip load (Figure D-30)","z":"depth"}),
 "D-4":("Angle δ for the strip load stress increase","δ = tan^-1((x−b)/z)",{}),
 "D-5":("Stress increase below the equivalent footing, compared with 10% to decide whether a depth increment is included in the settlement sum","Stress Increase = (σ'1(ss+e) − σ'vo)/σ'vo * 100%",{"σ'vo":"initial vertical effective stress","σ'1(ss+e)":"new vertical effective stress below the equivalent footing"}),
 "D-6":("Cost per linear foot of pile section (the text names it Equation D-5)","Cost = ($/lbs) * (lbs/ft)",{"$":"cost per pound of steel, $0.90/lb","w":"weight per linear foot of pile section"}),
 "D-7":("Tolerable differential settlement between substructure supports","Sd = A * Ls",{"Sd":"tolerable differential settlement","A":"angular distortion limit, 0.004 radians (Table 7-18)","Ls":"span length"}),
}
EQ_PAGE={"D-1":54,"D-2":64,"D-3":64,"D-4":64,"D-5":69,"D-6":85,"D-7":166}
def rows_resist(cells, labels):
    # two side-by-side column groups of 4: depth, shaft, toe, nominal
    nums=[c for c in cells if re.fullmatch(r'[\d.,]+',c)]
    assert len(nums)%4==0, len(nums)
    rows=[nums[k:k+4] for k in range(0,len(nums),4)]
    # print order: left row, right row alternate -> sort by depth
    rows.sort(key=lambda r: float(r[0].replace(',','')))
    return rows
STRUCT={"D-6","D-51","D-100"}
def table_entry(tid,title,cells,pages):
    pg=pages[0]
    pr=f"p. {pages[0]}" if len(pages)==1 else f"pp. {pages[0]} to {pages[-1]}"
    if tid in STRUCT:
        rows=rows_resist(cells,None)
        desc=("Depth (feet) / Nominal Shaft Resistance (kips) / Nominal Toe Resistance (kips) / Nominal Geotechnical Resistance (kips), every row as printed ("+pr+"): "
              +"; ".join(" / ".join(r) for r in rows)+".")
    else:
        desc="Cells as printed, read across each row ("+pr+"): "+" | ".join(fix(c) for c in cells)
    return {"table_id":tid,"title":fix(title),"description":desc,"page":pg}
TITLES={"D.15":"Block 15: North Abutment – Establish Pile Penetration Depths that Satisfy Tolerable Deformations; Estimate Group Settlement over the Minimum and Maximum Range of Pile Penetration Depths From Blocks 12 through 14 and Identify All Pile Toe Elevations Which Result in Intolerable Deformations; If Conditions Warrant, Modify Design and Return to Block 10",
"D.27":"Block 15: Pier 2 – Establish Pile Penetration Depths that Satisfy Tolerable Deformations. Estimate Group Settlement over the Minimum and Maximum Range of Pile Penetration Depths From Blocks 12 to 14 and Identify All Pile Toe Elevations Which Result in Intolerable Deformations. If Conditions Warrant, Modify Design and Return to Block 10",
"D.39":"Block 15: South Abutment – Establish Pile Penetration Depths that Satisfy Tolerable Deformations. Estimate Group Settlement over the Minimum and Maximum Range of Pile Penetration Depths From Blocks 12 to 14 and Identify All Pile Toe Elevations Which Result in Intolerable Deformations. If Conditions Warrant, Modify Design and Return to Block 10"}
TAIL={"D.15":"Deformations; If Conditions Warrant, Modify Design and Return to Block 10","D.27":"If Conditions Warrant, Modify Design and Return to Block 10","D.39":"If Conditions Warrant, Modify Design and Return to Block 10"}
out=[]
def mk(sid,title,body,figs,tabs,eqs,p0,p1):
    return {"section_id":sid,"title":title,"body":body,"key_points":[],"equations":eqs,"figures":figs,"tables":tabs,
            "applicability":f"FHWA-NHI-16-009 (GEC-12) Volume III, Appendix D (Comprehensive Design Examples), printed pp. {p0} to {p1}." if p0!=p1 else f"FHWA-NHI-16-009 (GEC-12) Volume III, Appendix D (Comprehensive Design Examples), printed p. {p0}."}
# intro
itxt,ifigs,_,_=g12x.render(dict(lines=intro_lines+[(p,l) for p in range(36,42) for l in g12x.page_lines(p-1)]))
out.append(mk("D","Comprehensive Design Examples",collapse_pages(fix(itxt.replace("APPENDIX D COMPREHENSIVE DESIGN EXAMPLES","",1).strip())),
   [{"figure_id":"D-1","title":"Design process flow chart.","description":"printed on pp. 2 to 7","page":2}],[],[],1,7))
for n,s in enumerate(secs):
    txt,figs,tabs,eqs=g12x.render(s)
    pages=sorted({pg-OFF for pg,_ in s['lines']}) or [s['page']-OFF]
    p0=s['page']-OFF; p1=max(pages+[p0])
    # merge multi-page tables
    T={}
    for t in tabs:
        e=T.setdefault(t['table_id'],dict(title=t['title'],cells=[],pages=[]))
        if e['pages'] and e['cells']:
            # drop repeated header on continuation page
            c=t['cells']; k=0
            while k<len(c) and not re.fullmatch(r'[\d.,]+',c[k]): k+=1
            e['cells']+=c[k:] if t['table_id'] in STRUCT else c
        else: e['cells']+=t['cells']
        e['pages'].append(t['page'])
    tabl=[table_entry(k,v['title'],v['cells'],sorted(set(v['pages']))) for k,v in T.items()]
    F={}
    for fid,cap,pg in figs: F.setdefault(fid,(fix(cap),pg))
    figl=[{"figure_id":k,"title":v[0],"description":"","page":v[1]} for k,v in F.items()]
    eql=[]
    HOME={"D-1":"D.13","D-2":"D.15","D-3":"D.15","D-4":"D.15","D-5":"D.15","D-6":"D.19","D-7":"D.30"}
    for e in dict.fromkeys(eqs):
        if e in EQS and HOME[e]==s['sid']:
            d,f,v=EQS[e]; eql.append({"eq_id":e,"description":d,"formula":f,"variables":v,"notes":f"p. {EQ_PAGE[e]}","implemented_in":None})
    body=collapse_pages(fix(txt))
    if s['sid']=='D.19': body=body.replace("Puu","Pui")
    if s['sid']=='D.23': body=body.replace("Puu","Puz")
    title=fix(s['title'])
    if s['sid'] in TITLES:
        title=TITLES[s['sid']]
        body=re.sub(r'^(\[p\. \d+\] )'+re.escape(TAIL[s['sid']])+' ',r'\1',body)
        assert not body.split('] ',1)[1].startswith(TAIL[s['sid']][:10]), s['sid']
    out.append(mk(s['sid'],title,body,figl,tabl,eql,p0,p1))
data={"reference_id":"FHWA-NHI-16-009","reference_title":"Design and Construction of Driven Pile Foundations","volume":3,"chapter":22,
      "chapter_title":"Appendix D: Comprehensive Design Examples","sections":out}
json.dump(data,open(sys.argv[1],"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(len(out), sum(len(s['tables']) for s in out), sum(len(s['figures']) for s in out), sum(len(s['equations']) for s in out), sum(len(s['body']) for s in out))

# ---- split sections that would not fit the reference tools (as build_printed_text.split_long)
LIMIT=11500
def jlen(x): return len(json.dumps(x,ensure_ascii=False))
def part_objs(sec,text,pages):
    tabs=[t for t in sec['tables'] if f"[Table {t['table_id']}]" in text]
    figs=[f for f in sec['figures'] if f['page'] in pages]
    eqs=[e for e in sec['equations'] if f"[Eq. {e['eq_id']}]" in text]
    return tabs,figs,eqs
final=[]
for sec in data['sections']:
    if jlen(sec)<=LIMIT: final.append(sec); continue
    units=re.split(r'(?=\[p\. \d+\])',sec['body']); units=[u.strip() for u in units if u.strip()]
    chunks=[];cur=[]
    def size(us):
        text=" ".join(us); pages={int(p) for p in re.findall(r'\[p\. (\d+)\]',text)}
        t,f,e=part_objs(sec,text,pages)
        return jlen(dict(sec,body=text,tables=t,figures=f,equations=e))+200
    for u in units:
        if cur and size(cur+[u])>LIMIT: chunks.append(cur); cur=[]
        cur.append(u)
    if cur: chunks.append(cur)
    starts=[int(re.findall(r'\[p\. (\d+)\]'," ".join(ch))[0]) for ch in chunks]
    endp=max([starts[-1]]+[f['page'] for f in sec['figures']]+[t['page'] for t in sec['tables']])
    for n,ch in enumerate(chunks):
        text=" ".join(ch); pl=[int(p) for p in re.findall(r'\[p\. (\d+)\]',text)]
        hi=starts[n+1]-1 if n+1<len(chunks) else endp
        pages=set(range(pl[0],max(hi,pl[-1])+1)); t,f,e=part_objs(sec,text,pages)
        pr=f"p. {pl[0]}" if pl[0]==pl[-1] else f"pp. {pl[0]} to {pl[-1]}"
        part=dict(sec,body=text,tables=t,figures=f,equations=e)
        if n:
            letter=chr(ord('a')+n-1)
            part.update(section_id=f"{sec['section_id']}.{letter}",title=f"{sec['title']} (continued, {pr})",
                applicability=f"Part {n+1} of printed Section {sec['section_id']} ({pr}); the letter is not printed, the section is split here to fit the reference tools.")
        else:
            part['applicability']=f"FHWA-NHI-16-009 (GEC-12) Volume III, Appendix D (Comprehensive Design Examples), printed {pr} (Part 1 of printed Section {sec['section_id']}; the rest follows as lettered parts, split to fit the reference tools)."
        assert jlen(part)<=13000, (part['section_id'],jlen(part))
        final.append(part)
    # every object kept
    got=[(k,o) for p in final if p['section_id'].split('.')[:len(sec['section_id'].split('.'))]==sec['section_id'].split('.') for k in ('tables','figures','equations') for o in p[k]]
    need=[(k,o) for k in ('tables','figures','equations') for o in sec[k]]
    for x in need: assert x in got, (sec['section_id'],x[1].get('table_id') or x[1].get('figure_id') or x[1].get('eq_id'))
data['sections']=final
json.dump(data,open(sys.argv[1],"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print("after split",len(final),max(jlen(s) for s in final))

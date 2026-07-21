# -*- coding: utf-8 -*-
import pdfplumber, json, io, re, os
AQUI=os.path.dirname(os.path.abspath(__file__))
D=os.path.join(os.path.dirname(AQUI),"fontes")+"/"

def lines(f):
    out=[]
    with pdfplumber.open(D+f) as pdf:
        for p in pdf.pages: out += (p.extract_text() or "").split("\n")
    out=[l.rstrip() for l in out if "Moises.ai" not in l]
    if out and out[0].strip(): out=out[1:]
    if out and out[0].startswith("Key:"): out=out[1:]
    while out and not out[0].strip(): out=out[1:]
    return out

raw={
 "carcara": lines("Carcara___Festa_chords.pdf"),
 "animais": lines("Como_2_animais_chords.pdf"),
 "engoma":  lines("Enquanto_engoma_a_cal_a_chords.pdf"),
 "espumas": lines("Espumas_ao_vento_chords.pdf"),
 "galope":  lines("Galope_Razante___Estrala_Miuda___Sujeito_de_Sorte_chords (4).pdf"),
 "homem_preco": lines("mais_um_homem_apaixonado___Esse___meu_pre_o_chords.pdf"),
 "sete_tonem":  lines("sete_meninas___to_nem_ai_chords.pdf"),
 "alegria": lines("Alegria_Demais_chords.pdf"),
 "vozvento": lines("Dominguinhos___10___Voz_do_Vento_chords.pdf"),
 "zumzum": lines("Andre__Prando___Zum_zum_zum__feat_Juliana_Linhares____Andre__Prando___oficial__youtube__chords.pdf"),
 "esverdear": lines("Esverdear_chords.pdf"),
 "erroeu": lines("_Erro_eu_chords.pdf"),
 "heranca": lines("Heranc_a_De_Meu_Pai___Jackson_do_Pandeiro__youtube___1__chords.pdf"),
 "lucro": lines("Lucro_chords.pdf"),
 "fuxiqueira": lines("Sanfona_Fuxiqueira___Beni_cio_Guimara_es__youtube__chords.pdf"),
}

def split_at(key, needle):
    L=raw[key]
    i=[k for k,l in enumerate(L) if needle in l][0]
    # recua pra pegar a linha de acordes imediatamente acima
    j=i-1 if i>0 and L[i-1].strip() else i
    return L[:j], L[j:]

homem, preco = split_at("homem_preco", "Salta seu querido")
sete,  tonem = split_at("sete_tonem",  "Vou subir por aqui")

parts={"carcara":raw["carcara"],"animais":raw["animais"],"engoma":raw["engoma"],
       "espumas":raw["espumas"],"galope":raw["galope"],
       "homem":homem,"preco":preco,"sete":sete,"tonem":tonem,
       "alegria":raw["alegria"],"vozvento":raw["vozvento"],"zumzum":raw["zumzum"],
       "esverdear":raw["esverdear"],"erroeu":raw["erroeu"],
       "heranca":raw["heranca"],"lucro":raw["lucro"],"fuxiqueira":raw["fuxiqueira"]}

# ---------- filtro de fala de palco / ruído de transcrição ----------
BANTER = [
 "Antes de começar com mais uma música minha",
 "pro povo não sair falando por aí que eu só toco shot",
 "Salta seu querido",
 "Diversificado, só pra fingir que não é um black",
 "Toca demais esse baixista",
 "Oi Glau",
 "Conhecer essa música com o mestrezinho",
 "De letra, né?",
 "Nossa galera, galera também queria uma salva de palmas",
 "técnico de São",
 "o nosso\ntécnico",
 "Ai tu brilha, véi",
 "(cantarola)",
 "Estrelar-me o dar",
]
INLINE = [
 (r"\s*\((?:bate outra[^)]*|vai, vai, vai|ele é chato[^)]*|recapitulo|nem aí|eu 'tô nem aí|pega!)\)", ""),
 (r",?\s*né\?\s*$", ""),
 (r",\s*pega!", ""),
]

CH = re.compile(r"^([A-G](?:#|b)?)((?:maj|min|m|M|aug|dim|sus|add)?[0-9#b+\-/A-Ga-z]*)$")
def is_chord_line(l):
    t=l.strip()
    if not t: return False
    k=t.split()
    return len(k)<=16 and all(CH.match(x) for x in k)

out={}
for k,L in parts.items():
    skip=[]
    clean=[]
    for i,l in enumerate(L):
        hit = any(b in l for b in BANTER)
        # continuacao de fala que quebrou linha (linha curta logo apos uma fala)
        if not hit and skip and skip[-1]==i-1 and not is_chord_line(l) and len(l.strip())<40 \
           and any(b in L[i-1] for b in ["salva de palmas","técnico de São"]):
            hit=True
        if not hit and i>0 and "salva de palmas" in L[i-1]: hit=True
        if hit: skip.append(i)
        c=l
        if not is_chord_line(l):
            for pat,rep in INLINE: c=re.sub(pat,rep,c)
        clean.append(c.rstrip())
    out[k]={"raw":"\n".join(L),"clean":"\n".join(clean),"skip":skip}

io.open(os.path.join(AQUI,"_cache_cifras.json"),"w",encoding="utf-8").write(json.dumps(out,ensure_ascii=False))
for k,v in out.items():
    print(f"{k:9s} linhas={len(v['raw'].splitlines()):4d}  falas filtradas={len(v['skip'])}")

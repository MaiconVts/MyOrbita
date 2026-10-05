# Banner do README

Gera `docs/assets/banner.svg` (SVG animado em CSS, sem script, compatível com `<img>` do GitHub).

```bash
cd tools/banner
pip install numpy pillow uharfbuzz fonttools
python nebula.py      # textura de nebulosas (nebula_preview.png)
python gen_banner.py  # monta o SVG final
```

Fontes: Unbounded e Manrope (SIL Open Font License), em `fonts/`.

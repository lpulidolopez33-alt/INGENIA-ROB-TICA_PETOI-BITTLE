"""Renderiza H1 vigente. Dependencia opcional: reportlab==4.4.9; no se usa al ejecutar la app."""
from pathlib import Path
import re
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

ROOT = Path(__file__).resolve().parents[1]


def main():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('Texto', fontName='Helvetica', fontSize=10, leading=14, spaceAfter=7))
    styles.add(ParagraphStyle('Celda', parent=styles['Texto'], fontSize=9, leading=12, spaceAfter=0))
    styles['Heading1'].fontSize = 15
    styles['Heading1'].textColor = colors.HexColor('#194b59')
    styles['Title'].fontSize = 24
    def fmt(s):
        s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', s)
        return escape(s.replace('**', '').replace('`', '').replace('→', ' > ').replace('–', '-'))
    def para(s, style='Texto'):
        return Paragraph(fmt(s), styles[style])
    lines = (ROOT / 'docs/h1/H1_v0.4.md').read_text(encoding='utf-8').splitlines()
    story, buf = [], []
    def flush():
        if buf:
            story.append(para(' '.join(buf)))
            buf.clear()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('|'):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [c.strip() for c in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r'[-:]+', c) for c in cells):
                    rows.append(cells)
                i += 1
            if len(rows[0]) > 4:
                for row in rows[1:]:
                    card = [para(row[0], 'Heading3')]
                    for heading, value in zip(rows[0][1:], row[1:]):
                        card.append(para(f'{heading}: {value}'))
                    story.append(KeepTogether(card))
            else:
                count = len(rows[0])
                widths = {2: [55, 450], 3: [100, 200, 205], 4: [55, 95, 270, 85]}[count]
                table = Table([[para(c, 'Celda') for c in row] for row in rows], colWidths=widths, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0edf0')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LINEBELOW', (0, 0), (-1, -1), .3, colors.HexColor('#c0cbd0')),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
                story += [table, Spacer(1, 10)]
            continue
        elif line.startswith('#'):
            flush()
            story.append(para(line.lstrip('# ').strip(), 'Title' if line.startswith('# ') else 'Heading1'))
        elif not line.strip():
            flush()
        else:
            buf.append(line)
        i += 1
    flush()
    def footer(canvas, doc):
        canvas.setFont('Helvetica', 8)
        canvas.drawString(45, 25, 'ARGOS | VOICE-BITTLE | H1 v0.4 | 13/11/2026')
        canvas.drawRightString(A4[0]-45, 25, str(doc.page))
    SimpleDocTemplate(str(ROOT / 'docs/h1/H1_v0.4.pdf'), pagesize=A4,
                      rightMargin=45, leftMargin=45, topMargin=42, bottomMargin=42,
                      title='VOICE-BITTLE H1 v0.4', author='Equipo ARGOS').build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == '__main__':
    main()

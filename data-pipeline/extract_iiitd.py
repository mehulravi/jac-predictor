"""
extract_iiitd.py — IIIT-D's tables are the trickiest in the dataset:
- each branch has TWO sub-columns (JEE Rank, IIIT Rank)
- rows with a priority note span 3 physical text lines (JEE value above,
  category label + IIIT value on the middle line, "(vi)" suffix below)
- the page holds two tables stacked: "Without Bonus" and "With Bonus"

Strategy: use nearest-neighbour snapping twice — first snap every word to
the nearest CATEGORY ROW by vertical position (top), then snap every word
within that row to the nearest COLUMN by horizontal position (x0). This
sidesteps the irregular multi-line row heights entirely.
"""
import pdfplumber
import re

import os
# Put jac_merged.pdf in this folder, or set JAC_PDF_PATH to its location.
PDF_PATH = os.environ.get('JAC_PDF_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jac_merged.pdf'))

CATEGORY_PATTERN = re.compile(r'^(GN|EW|OB|SC|ST)(KM|[A-Z]{3})$')


def extract_iiitd_table(page_index, section='without_bonus'):
    with pdfplumber.open(PDF_PATH) as pdf:
        page = pdf.pages[page_index]
        words = page.extract_words()

    without_top = next(w['top'] for w in words if w['text'] == 'Without')
    with_top = next((w['top'] for w in words if w['text'] == 'With' and w['top'] > without_top), None)
    note_top = next((w['top'] for w in words if w['text'] == 'Note:'), 10**6)

    if section == 'without_bonus':
        region_words = [w for w in words if without_top < w['top'] < (with_top or note_top)]
    else:
        region_words = [w for w in words if with_top and with_top < w['top'] < note_top]

    branch_header_top = min(w['top'] for w in region_words if w['text'] == 'Category')
    branch_words = [w for w in region_words if abs(w['top'] - branch_header_top) <= 2 and w['text'] != 'Category']

    label_words = [w for w in region_words if branch_header_top < w['top'] < branch_header_top + 30]
    jee_x = sorted(w['x0'] for w in label_words if w['text'] == 'JEE')
    iiit_x = sorted(w['x0'] for w in label_words if w['text'] == 'IIIT')

    branch_x = sorted(set(w['x0'] for w in branch_words))
    columns = []
    for bx in branch_x:
        bname = next(w['text'] for w in branch_words if abs(w['x0'] - bx) < 3)
        j = min(jee_x, key=lambda x: abs(x - bx)) if jee_x else None
        i_candidates = [x for x in iiit_x if x > bx - 5]
        i = min(i_candidates, key=lambda x: abs(x - (j + 44 if j else bx))) if i_candidates else None
        if j is not None:
            columns.append((bname, 'JEE', j))
            jee_x.remove(j)
        if i is not None:
            columns.append((bname, 'IIIT', i))
            iiit_x.remove(i)
    columns.sort(key=lambda c: c[2])

    data_start_top = branch_header_top + 30
    cat_words = [w for w in region_words
                 if w['top'] > data_start_top and w['x0'] < 100 and CATEGORY_PATTERN.match(w['text'])]
    cat_rows = sorted([(w['top'], w['text']) for w in cat_words], key=lambda t: t[0])

    if not cat_rows:
        return columns, {}

    value_words = [w for w in region_words
                   if w['top'] > data_start_top and not (w['x0'] < 100 and CATEGORY_PATTERN.match(w['text']))]

    row_tops = [t for t, _ in cat_rows]
    row_labels = [c for _, c in cat_rows]
    col_x = [c[2] for c in columns]

    def nearest_row(top):
        return min(range(len(row_tops)), key=lambda i: abs(row_tops[i] - top))

    def nearest_col(x0):
        return min(range(len(col_x)), key=lambda i: abs(col_x[i] - x0))

    # Numbers and their "(...)" priority suffixes are snapped to row+column
    # INDEPENDENTLY (both by nearest row-top and nearest column-x0), rather
    # than by adjacency to each other -- adjacency proximity is ambiguous
    # near the right edge where a suffix can sit closer to the next column's
    # number than to its own column's header x-position.
    results = {label: {f"{b}_{m}": None for b, m, _ in columns} for label in row_labels}
    priorities = {label: {b: None for b, _, _ in columns} for label in row_labels}

    for w in value_words:
        ri = nearest_row(w['top'])
        ci = nearest_col(w['x0'])
        b, m, _ = columns[ci]
        label = row_labels[ri]
        if re.match(r'^\d', w['text']):
            results[label][f"{b}_{m}"] = w['text']
        elif w['text'].startswith('('):
            priorities[label][b] = w['text'].strip('()')

    # attach priority note (from whichever sub-column it snapped nearest to)
    # onto both the JEE and IIIT values for that branch+category
    for label in row_labels:
        for b, m, _ in columns:
            pri = priorities[label].get(b)
            if pri and results[label].get(f"{b}_{m}"):
                results[label][f"{b}_{m}"] = f"{results[label][f'{b}_{m}']} ({pri})"

    return columns, results


if __name__ == "__main__":
    import sys
    import json
    page_index = int(sys.argv[1])
    section = sys.argv[2] if len(sys.argv) > 2 else 'without_bonus'
    cols, res = extract_iiitd_table(page_index, section)
    print("COLUMNS:", [c[0] + '_' + c[1] for c in cols])
    print(json.dumps(res, indent=2))

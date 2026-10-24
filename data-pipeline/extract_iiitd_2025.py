"""
extract_iiitd_2025.py — IIIT-D's 2025 bulletin only publishes IIITD Rank
per branch (no JEE CRL reference, unlike 2024's dual-column tables). One
column per branch instead of two, but still uses the same multi-line-row
structure as 2024, so the same row/column independent-snapping strategy applies.
"""
import pdfplumber
import re

import os
# Put jac_merged.pdf in this folder, or set JAC_PDF_PATH to its location.
PDF_PATH = os.environ.get('JAC_PDF_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jac_merged.pdf'))
CATEGORY_PATTERN = re.compile(r'^(GN|EW|OB|SC|ST)(KM|[A-Z]{3})$')


def extract_iiitd_2025_table(page_index, section='without_bonus'):
    with pdfplumber.open(PDF_PATH) as pdf:
        page = pdf.pages[page_index]
        words = page.extract_words()

    without_top = next(w['top'] for w in words if w['text'] == 'Without')
    with_top = next((w['top'] for w in words if w['text'] == 'With' and w['top'] > without_top), None)
    note_top = next((w['top'] for w in words if w['text'].startswith('Note')), 10**6)

    if section == 'without_bonus':
        region_words = [w for w in words if without_top < w['top'] < (with_top or note_top)]
    else:
        region_words = [w for w in words if with_top and with_top < w['top'] < note_top]

    if not region_words:
        return [], {}

    branch_header_top = min(w['top'] for w in region_words if w['text'] == 'Category')
    branch_words = [w for w in region_words if abs(w['top'] - branch_header_top) <= 2 and w['text'] != 'Category']
    branches = [(w['text'], w['x0']) for w in sorted(branch_words, key=lambda w: w['x0'])]

    data_start_top = branch_header_top + 25
    cat_words = [w for w in region_words
                 if w['top'] > data_start_top and w['x0'] < 100 and CATEGORY_PATTERN.match(w['text'])]
    cat_rows = sorted([(w['top'], w['text']) for w in cat_words], key=lambda t: t[0])
    if not cat_rows:
        return branches, {}

    value_words = [w for w in region_words
                   if w['top'] > data_start_top and not (w['x0'] < 100 and CATEGORY_PATTERN.match(w['text']))]

    row_tops = [t for t, _ in cat_rows]
    row_labels = [c for _, c in cat_rows]
    col_x = [x for _, x in branches]
    col_names = [n for n, _ in branches]

    def nearest_row(top):
        return min(range(len(row_tops)), key=lambda i: abs(row_tops[i] - top))

    def nearest_col(x0):
        return min(range(len(col_x)), key=lambda i: abs(col_x[i] - x0))

    results = {label: {b: None for b in col_names} for label in row_labels}
    priorities = {label: {b: None for b in col_names} for label in row_labels}

    for w in value_words:
        ri = nearest_row(w['top'])
        ci = nearest_col(w['x0'])
        label, b = row_labels[ri], col_names[ci]
        if re.match(r'^\d', w['text']):
            results[label][b] = w['text']
        elif w['text'].startswith('('):
            priorities[label][b] = w['text'].strip('()')

    for label in row_labels:
        for b in col_names:
            pri = priorities[label].get(b)
            if pri and results[label].get(b):
                results[label][b] = f"{results[label][b]} ({pri})"

    return branches, results


if __name__ == "__main__":
    import sys
    import json
    page_index = int(sys.argv[1])
    section = sys.argv[2] if len(sys.argv) > 2 else 'without_bonus'
    branches, res = extract_iiitd_2025_table(page_index, section)
    print("BRANCHES:", [b[0] for b in branches])
    print(json.dumps(res, indent=2))

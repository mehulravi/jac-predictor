"""
extract_iiitd_2025_r5.py — page 28 (index 27) has branch names one line
ABOVE the 'Category'/'JEE Rank'/'IIITD Rank' label row, unlike every other
IIIT-D page where they share a row. Same row/column snapping strategy as
extract_iiitd.py, just with branch-name detection corrected for this layout.
"""
import pdfplumber
import re

import os
# Put jac_merged.pdf in this folder, or set JAC_PDF_PATH to its location.
PDF_PATH = os.environ.get('JAC_PDF_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jac_merged.pdf'))
KNOWN_BRANCHES = {'CSAM', 'CSAI', 'CSB', 'CSD', 'CSEcon', 'CSE', 'CSSS', 'EVE', 'ECE'}

# This page's text layer has a kerning artifact that merges some category
# labels with stray trailing characters (e.g. 'OBGNO' -> 'OBGNOD',
# 'GNKM' -> 'GNKMAI'). Match by known-valid-code prefix instead of a
# regex, so these rows aren't silently dropped (which was causing their
# data to bleed into neighboring rows via nearest-row snapping).
VALID_CODES = [
    'OBCWD', 'OBGND', 'OBGNO', 'EWCWD', 'EWGND', 'EWGNO', 'EWPDD', 'GNKM',
    'GNCWD', 'GNGND', 'GNGNO', 'GNPDD', 'SCCWD', 'SCGND', 'SCGNO', 'STCWD',
    'STGND', 'STGNO', 'STPDD',
]
VALID_CODES.sort(key=len, reverse=True)  # match longest/most-specific first


def normalize_category_label(text):
    for code in VALID_CODES:
        if text.startswith(code):
            return code
    return None


def extract(page_index, section='without_bonus'):
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

    # branch names: the row of known branch codes near the top of the region
    branch_words = sorted([w for w in region_words if w['text'] in KNOWN_BRANCHES], key=lambda w: w['top'])
    branch_row_top = branch_words[0]['top']
    branch_words = [w for w in branch_words if abs(w['top'] - branch_row_top) <= 2]
    branch_words.sort(key=lambda w: w['x0'])

    # sub-header row (JEE Rank / IIITD Rank) is the next distinct row below
    sub_header_top = min(w['top'] for w in region_words
                          if w['top'] > branch_row_top + 2 and w['text'] in ('JEE', 'IIITD'))
    jee_x = sorted(w['x0'] for w in region_words if abs(w['top'] - sub_header_top) <= 2 and w['text'] == 'JEE')
    iiit_x = sorted(w['x0'] for w in region_words if abs(w['top'] - sub_header_top) <= 2 and w['text'] == 'IIITD')

    columns = []  # (branch, metric, x0)
    for bw in branch_words:
        j_candidates = [x for x in jee_x if x >= bw['x0'] - 5]
        i_candidates = [x for x in iiit_x if x >= bw['x0'] - 5]
        j = min(j_candidates) if j_candidates else None
        i = min([x for x in i_candidates if j is None or x > j], default=(i_candidates[0] if i_candidates else None))
        if j is not None:
            columns.append((bw['text'], 'JEE', j))
            jee_x.remove(j)
        if i is not None:
            columns.append((bw['text'], 'IIITD', i))
            iiit_x.remove(i)
    columns.sort(key=lambda c: c[2])

    data_start_top = sub_header_top + 5
    cat_words_raw = [w for w in region_words if w['top'] > data_start_top and w['x0'] < 70]
    cat_rows = []
    for w in sorted(cat_words_raw, key=lambda w: w['top']):
        normalized = normalize_category_label(w['text'])
        if normalized:
            cat_rows.append((w['top'], normalized))
    if not cat_rows:
        return columns, {}

    value_words = [w for w in region_words
                   if w['top'] > data_start_top and w['x0'] >= 70]

    row_tops = [t for t, _ in cat_rows]
    row_labels = [c for _, c in cat_rows]
    col_x = [c[2] for c in columns]

    def nearest_row(top):
        return min(range(len(row_tops)), key=lambda i: abs(row_tops[i] - top))

    def nearest_col(x0):
        return min(range(len(col_x)), key=lambda i: abs(col_x[i] - x0))

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
    cols, res = extract(page_index, section)
    print("COLUMNS:", [c[0] + '_' + c[1] for c in cols])
    print(json.dumps(res, indent=2))

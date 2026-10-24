"""
extract_dtu2025.py — DTU's 2025 tables use the same coded-column scheme as
NSUT (GNGND, GNGLD, ...), decodable via decode.py. Unlike NSUT, DTU's row
labels are multi-word branch names (not a single token), so rows are keyed
by the numeric S.No. column instead, then mapped to branch names by a
fixed, doc-verified order.
"""
import pdfplumber
import re

import os
# Put jac_merged.pdf in this folder, or set JAC_PDF_PATH to its location.
PDF_PATH = os.environ.get('JAC_PDF_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jac_merged.pdf'))
CODE_PATTERN = re.compile(r'^(GN|EW|OB|SC|ST)[A-Z]{2,3}$|^KM$')

BRANCH_ORDER = [
    'Computer Science and Engineering',
    'Computer Science and Engineering (Data Science & Analytics)',
    'Information Technology',
    'Information Technology (Cyber Security)',
    'Software Engineering',
    'Mathematics and Computing',
    'Electronics and Communication Engineering',
    'Electronics Engineering (VLSI Design and Technology)',
    'Electrical Engineering',
    'Mechanical Engineering',
    'Mechanical Engineering with specialization in Automotive Engineering',
    'Engineering Physics',
    'Chemical Engineering',
    'Civil Engineering',
    'Production & Industrial Engineering',
    'Environmental Engineering',
    'Bio-Technology',
]


def extract_dtu2025_region(page_index):
    with pdfplumber.open(PDF_PATH) as pdf:
        page = pdf.pages[page_index]
        words = page.extract_words()

    header_top = min(w['top'] for w in words if w['text'] == 'S.No.')
    header_words = [w for w in words if abs(w['top'] - header_top) <= 2 and CODE_PATTERN.match(w['text'])]
    columns = sorted([(w['text'], w['x0']) for w in header_words], key=lambda c: c[1])

    data_start_top = header_top + 8
    sno_x0 = next(w['x0'] for w in words if w['text'] == 'S.No.')
    sno_words = [w for w in words
                 if w['top'] > data_start_top and abs(w['x0'] - sno_x0) < 20 and re.match(r'^\d+$', w['text'])]
    row_tops = sorted(set(w['top'] for w in sno_words))

    stop_words = [w for w in words if w['text'] in ('Kashmiri', 'Defense', 'Defence')]
    stop_top = min((w['top'] for w in stop_words if w['top'] > data_start_top), default=10**6)
    row_tops = [t for t in row_tops if t < stop_top]

    value_words = [w for w in words
                   if data_start_top < w['top'] < stop_top and w['x0'] > sno_x0 + 20]

    col_x = [c[1] for c in columns]
    col_names = [c[0] for c in columns]

    def nearest_row(top):
        return min(range(len(row_tops)), key=lambda i: abs(row_tops[i] - top))

    def nearest_col(x0):
        return min(range(len(col_x)), key=lambda i: abs(col_x[i] - x0))

    results = {i + 1: {c: None for c in col_names} for i in range(len(row_tops))}
    for w in value_words:
        if not re.match(r'^\d', w['text']):
            continue
        ri = nearest_row(w['top'])
        ci = nearest_col(w['x0'])
        results[ri + 1][col_names[ci]] = w['text']

    named_results = {}
    for i, branch_name in enumerate(BRANCH_ORDER):
        if (i + 1) in results:
            named_results[branch_name] = results[i + 1]

    return columns, named_results


if __name__ == "__main__":
    import sys
    import json
    page_index = int(sys.argv[1])
    cols, res = extract_dtu2025_region(page_index)
    print("COLUMNS:", [c[0] for c in cols])
    print(json.dumps(res, indent=2))

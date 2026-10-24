"""
extract_table.py — parses a wide, sparse cutoff table from the PDF by using
each word's actual x-coordinate (from pdfplumber) and snapping it to the
nearest header column. This avoids the ambiguity of guessing which blank
gap a lone number belongs to when eyeballing text/images.

Usage: edit PAGE_INDEX and BRANCH_CODES for the table you're extracting,
then run. Prints a dict you can paste into a build_*.py script.
"""
import pdfplumber
import re

import os
# Put jac_merged.pdf in this folder, or set JAC_PDF_PATH to its location.
PDF_PATH = os.environ.get('JAC_PDF_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jac_merged.pdf'))


def extract_table(page_index, branch_codes, y_tolerance=6):
    with pdfplumber.open(PDF_PATH) as pdf:
        page = pdf.pages[page_index]
        words = page.extract_words()

    # 1. find header row: the line containing 'Category' near top, followed
    #    by the actual column code words (GN.., EW.., OB.., SC.., ST.., KM)
    header_words = [w for w in words if re.match(r'^(GN|EW|OB|SC|ST|KM)[A-Z]{0,3}$', w['text'])]
    # header row is the one with the most such matches at a consistent 'top'
    from collections import Counter
    top_counts = Counter(round(w['top']) for w in header_words)
    header_top = top_counts.most_common(1)[0][0]
    header_cols = sorted(
        [w for w in header_words if abs(w['top'] - header_top) <= y_tolerance],
        key=lambda w: w['x0']
    )
    col_names = [w['text'] for w in header_cols]
    col_x = [w['x0'] for w in header_cols]

    # 2. restrict to the table body: below the header row, above the legend
    #    ("*East Campus Courses" / "Course Code" marks where the legend starts)
    legend_words = [w for w in words if w['text'] in ('*East', 'Course')]
    legend_top = min((w['top'] for w in legend_words), default=10**6)
    body_words = [w for w in words if header_top < w['top'] < legend_top]

    # 3. find each branch row's words (branch code word marks row start) —
    #    take only the FIRST (topmost) occurrence of each branch code in the body
    branch_word_objs = []
    seen = set()
    for w in sorted(body_words, key=lambda w: w['top']):
        code = w['text']
        if code.rstrip('*') in branch_codes and code not in seen:
            branch_word_objs.append(w)
            seen.add(code)

    results = {}
    for bw in branch_word_objs:
        code = bw['text']
        row_top = bw['top']
        # gather all words on same row (within tolerance), excluding the branch code itself
        row_words = sorted(
            [w for w in body_words if abs(w['top'] - row_top) <= y_tolerance and w['x0'] > bw['x0']],
            key=lambda w: w['x0']
        )
        # merge adjacent words that are close together (e.g. "750303" + "(I)")
        merged = []
        for w in row_words:
            # only merge a "(...)" priority suffix onto the previous number,
            # never merge two separate numeric values together
            if merged and w['text'].startswith('(') and (w['x0'] - merged[-1]['x1']) < 8:
                merged[-1]['text'] += ' ' + w['text']
                merged[-1]['x1'] = w['x1']
            else:
                merged.append(dict(w))

        row_result = {c: None for c in col_names}
        for w in merged:
            # snap to nearest header column
            best_i = min(range(len(col_x)), key=lambda i: abs(col_x[i] - w['x0']))
            row_result[col_names[best_i]] = w['text']
        results[code] = row_result

    return col_names, results


if __name__ == "__main__":
    import sys
    import json

    page_index = int(sys.argv[1])
    branch_codes = sys.argv[2].split(',')
    cols, res = extract_table(page_index, branch_codes)
    print("COLUMNS:", cols)
    print(json.dumps(res, indent=2))

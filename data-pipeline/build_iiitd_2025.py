"""
build_iiitd_2025.py — IIIT-D's 2025 data has an inconsistency worth noting:
Round 4 only publishes IIITD Rank (no JEE CRL reference at all), while
Round 5 publishes both, matching 2024's format. Both source tables are
handled by their respective extractors.
"""
import csv
import re
from extract_iiitd_2025 import extract_iiitd_2025_table
from extract_iiitd_2025_r5 import extract as extract_r5
from decode import decode_code

BRANCH_NAMES = {
    'CSAM': 'Computer Science and Applied Mathematics',
    'CSAI': 'Computer Science and Artificial Intelligence',
    'CSB': 'Computer Science and Biosciences',
    'CSD': 'Computer Science and Design',
    'CSE': 'Computer Science and Engineering',
    'CSSS': 'Computer Science and Social Sciences',
    'ECE': 'Electronics and Communications Engineering',
    'EVE': 'Electronics and VLSI Engineering',
    'CSEcon': 'Computer Science and Economics',  # new branch for 2025
}

rows = []


def clean(val):
    if val is None:
        return None, None
    m = re.match(r'^(\d+)\s*(?:\(([^)]+)\))?', val.strip())
    if not m:
        return None, None
    return int(m.group(1)), m.group(2)


def decode_cat(cat_code):
    if cat_code == 'GNKM':
        return {'category_code': 'GEN', 'quota_code': 'KASHMIRI_MIGRANT', 'region_code': None}
    return decode_code(cat_code)


# ---------------------------------------------------------------------
# Round 4 2025 — IIITD Rank only, single column per branch
# ---------------------------------------------------------------------
def process_r4(page_index, with_bonus, source_tag):
    branches, data = extract_iiitd_2025_table(page_index, 'with_bonus' if with_bonus else 'without_bonus')
    branch_names_found = [b for b, _ in branches]
    for cat_code, row in data.items():
        d = decode_cat(cat_code)
        for branch in branch_names_found:
            val, pri = clean(row.get(branch))
            if val is None:
                continue
            rows.append({
                'university': 'IIITD', 'branch_code': branch,
                'branch_name': BRANCH_NAMES.get(branch, branch),
                'year': 2025, 'round_number': 4,
                'category_code': d['category_code'], 'quota_code': d['quota_code'],
                'region_code': d['region_code'], 'rank_type': 'IIITD_RANK',
                'with_bonus': with_bonus, 'closing_rank': val,
                'priority_note': pri, 'source_page_ref': source_tag,
            })


# ---------------------------------------------------------------------
# Round 5 2025 — dual JEE/IIITD columns, same shape as 2024
# ---------------------------------------------------------------------
def process_r5(page_index, with_bonus, source_tag):
    section = 'with_bonus' if with_bonus else 'without_bonus'
    columns, data = extract_r5(page_index, section)
    branches = sorted(set(c[0] for c in columns))
    for cat_code, row in data.items():
        d = decode_cat(cat_code)
        for branch in branches:
            jee_val, jee_pri = clean(row.get(f"{branch}_JEE"))
            iiit_val, iiit_pri = clean(row.get(f"{branch}_IIITD"))
            priority = jee_pri or iiit_pri
            if jee_val is not None:
                rows.append({
                    'university': 'IIITD', 'branch_code': branch,
                    'branch_name': BRANCH_NAMES.get(branch, branch),
                    'year': 2025, 'round_number': 5,
                    'category_code': d['category_code'], 'quota_code': d['quota_code'],
                    'region_code': d['region_code'], 'rank_type': 'JEE_CRL',
                    'with_bonus': with_bonus, 'closing_rank': jee_val,
                    'priority_note': priority, 'source_page_ref': source_tag,
                })
            if iiit_val is not None:
                rows.append({
                    'university': 'IIITD', 'branch_code': branch,
                    'branch_name': BRANCH_NAMES.get(branch, branch),
                    'year': 2025, 'round_number': 5,
                    'category_code': d['category_code'], 'quota_code': d['quota_code'],
                    'region_code': d['region_code'], 'rank_type': 'IIITD_RANK',
                    'with_bonus': with_bonus, 'closing_rank': iiit_val,
                    'priority_note': priority, 'source_page_ref': source_tag,
                })


process_r4(20, False, 'IIITD_R4_2025_WithoutBonus')  # page 21
process_r4(20, True, 'IIITD_R4_2025_WithBonus')
process_r5(27, False, 'IIITD_R5_2025_WithoutBonus')  # page 28
process_r5(27, True, 'IIITD_R5_2025_WithBonus')

fieldnames = ['university', 'branch_code', 'branch_name', 'year', 'round_number',
              'category_code', 'quota_code', 'region_code', 'rank_type', 'with_bonus',
              'closing_rank', 'priority_note', 'source_page_ref']

with open('cutoffs_staging_iiitd_2025.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to cutoffs_staging_iiitd_2025.csv")

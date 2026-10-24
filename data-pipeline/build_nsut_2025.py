"""
build_nsut_2025.py — same approach as build_nsut.py, extended to 2025's
page numbers and its one new branch (B.Arch., West Campus).
"""
import csv
import re
from extract_table import extract_table
from decode import decode_code

BRANCH_NAMES = {
    'CSAI': 'Computer Science and Engineering (Artificial Intelligence)',
    'CSE': 'Computer Science and Engineering',
    'CSDS': 'Computer Science and Engineering (Data Science)',
    'IT': 'Information Technology',
    'ITNS': 'Information Technology (Network and Information Security)',
    'MAC': 'Mathematics and Computing',
    'ECE': 'Electronics and Communication Engineering',
    'EVDT': 'Electronics Engineering (VLSI Design and Technology)',
    'EE': 'Electrical Engineering',
    'ICE': 'Instrumentation and Control Engineering',
    'ME': 'Mechanical Engineering',
    'BT': 'Bio-Technology',
    'CSDA': 'Computer Science and Engineering (Big Data Analytics)',
    'CIOT': 'Computer Science and Engineering (Internet of Things)',
    'ECAM': 'Electronics and Communication Engineering (AI and Machine Learning)',
    'MEEV': 'Mechanical Engineering (Electric Vehicles)',
    'CE': 'Civil Engineering',
    'GI': 'Geoinformatics',
    'B.Arch.': 'Bachelor of Architecture',
}

CAMPUS_MAP = {
    'CSDA': 'East', 'CIOT': 'East', 'ECAM': 'East',
    'MEEV': 'West', 'CE': 'West', 'GI': 'West', 'B.Arch.': 'West',
}

BRANCH_CODES = list(BRANCH_NAMES.keys())

rows = []


def clean_num(val):
    if val is None:
        return None, None
    m = re.match(r'^(\d+)\s*(?:\(([^)]+)\))?', val.strip())
    if not m:
        return None, None
    return int(m.group(1)), m.group(2)


def process(page_index, year, rnd, source_tag):
    cols, data = extract_table(page_index, BRANCH_CODES)
    for branch_raw, values in data.items():
        branch = branch_raw.rstrip('*')
        name = BRANCH_NAMES[branch]
        campus = CAMPUS_MAP.get(branch)
        for col, raw_val in values.items():
            if raw_val is None:
                continue
            rank, priority = clean_num(raw_val)
            if rank is None:
                continue
            if col == 'KM':
                category_code, quota_code, region_code = 'GEN', 'KASHMIRI_MIGRANT', None
            else:
                decoded = decode_code(col)
                category_code = decoded['category_code']
                quota_code = decoded['quota_code']
                region_code = decoded['region_code']
            rows.append({
                'university': 'NSUT', 'campus': campus, 'branch_code': branch,
                'branch_name': name, 'year': year, 'round_number': rnd,
                'category_code': category_code, 'quota_code': quota_code,
                'region_code': region_code, 'closing_rank': rank,
                'priority_note': priority, 'source_page_ref': source_tag,
            })


process(16, 2025, 4, 'NSUT_R4_2025_Delhi')    # page 17
process(17, 2025, 4, 'NSUT_R4_2025_Outside')  # page 18
process(23, 2025, 5, 'NSUT_R5_2025_Delhi')    # page 24
process(24, 2025, 5, 'NSUT_R5_2025_Outside')  # page 25

fieldnames = ['university', 'campus', 'branch_code', 'branch_name', 'year', 'round_number',
              'category_code', 'quota_code', 'region_code', 'closing_rank',
              'priority_note', 'source_page_ref']

with open('cutoffs_staging_nsut_2025.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to cutoffs_staging_nsut_2025.csv")

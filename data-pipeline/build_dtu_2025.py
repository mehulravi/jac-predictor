"""
build_dtu_2025.py — DTU 2025 main tables (coded columns, GNGND-style) are
extracted via extract_dtu2025.py (coordinate/S.No.-based). The Defense (CW)
sub-tables use plain, unambiguous columns with explicit blanks, so they're
transcribed directly from pdftotext -layout output (verified against two
independent read-throughs).
"""
import csv
import re
from extract_dtu2025 import extract_dtu2025_region, BRANCH_ORDER
from decode import decode_code

rows = []

# Must match the short codes DTU's 2024 data uses, or the same physical
# branch would be stored as two different rows across years, breaking
# cross-year trend/reliability comparisons.
BRANCH_NAME_TO_CODE = {
    'Computer Science and Engineering': 'CSE',
    'Computer Science and Engineering (Data Science & Analytics)': 'CSDS',
    'Information Technology': 'IT',
    'Information Technology (Cyber Security)': 'ITCS',
    'Software Engineering': 'SE',
    'Mathematics and Computing': 'MCE',
    'Electronics and Communication Engineering': 'ECE',
    'Electronics Engineering (VLSI Design and Technology)': 'EVDT',
    'Electrical Engineering': 'EE',
    'Mechanical Engineering': 'ME',
    'Mechanical Engineering with specialization in Automotive Engineering': 'MAM',
    'Engineering Physics': 'EP',
    'Chemical Engineering': 'CHE',
    'Civil Engineering': 'CE',
    'Production & Industrial Engineering': 'PIE',
    'Environmental Engineering': 'ENE',
    'Bio-Technology': 'BT',
}


def add(branch_name, year, rnd, category_code, quota_code, region_code, rank, priority=None, source=''):
    if rank is None:
        return
    branch_code = BRANCH_NAME_TO_CODE.get(branch_name, branch_name)
    rows.append({
        'university': 'DTU', 'branch_code': branch_code, 'branch_name': branch_name,
        'year': year, 'round_number': rnd, 'category_code': category_code,
        'quota_code': quota_code, 'region_code': region_code,
        'closing_rank': rank, 'priority_note': priority, 'source_page_ref': source,
    })


def clean(val):
    if val is None:
        return None, None
    m = re.match(r'^(\d+)\s*(?:\(([^)]+)\))?', val.strip())
    if not m:
        return None, None
    return int(m.group(1)), m.group(2)


def load_main_table(page_index, year, rnd, source):
    columns, data = extract_dtu2025_region(page_index)
    for branch_name, values in data.items():
        for col, raw_val in values.items():
            rank, priority = clean(raw_val)
            if rank is None:
                continue
            d = decode_code(col)
            add(branch_name, year, rnd, d['category_code'], d['quota_code'], d['region_code'],
                rank, priority, source)


# Main tables (Delhi + Outside), R4 and R5
load_main_table(18, 2025, 4, 'DTU_R4_2025_Delhi')     # page 19
load_main_table(19, 2025, 4, 'DTU_R4_2025_Outside')   # page 20
load_main_table(25, 2025, 5, 'DTU_R5_2025_Delhi')     # page 26
load_main_table(26, 2025, 5, 'DTU_R5_2025_Outside')   # page 27

# ---------------------------------------------------------------------
# Defense (CW) tables — transcribed from pdftotext -layout (plain,
# unambiguous columns; verified against the source twice)
# ---------------------------------------------------------------------
DTU_R4_2025_DELHI_CW = {
    'Computer Science and Engineering': {'GNCWD': (205133, 'V(v)'), 'EWCWD': (102477, 'VI'), 'OBCWD': (86912, 'VI'), 'SCCWD': (193378, 'VIII'), 'STCWD': (476260, 'VI')},
    'Computer Science and Engineering (Data Science & Analytics)': {'GNCWD': (88380, 'V(vii)'), 'EWCWD': (115837, 'VI'), 'OBCWD': (95366, 'VI'), 'SCCWD': (415350, 'VIII')},
    'Information Technology': {'GNCWD': (362645, 'V(x)'), 'OBCWD': (143686, 'VI')},
    'Information Technology (Cyber Security)': {'GNCWD': (393724, 'V(vii)'), 'EWCWD': (118959, 'VI'), 'SCCWD': (839253, 'VIII')},
    'Software Engineering': {'GNCWD': (1261139, 'V(x)'), 'EWCWD': (137016, 'VI'), 'OBCWD': (160204, 'VI'), 'SCCWD': (394754, 'VIII')},
    'Mathematics and Computing': {'GNCWD': (24086, 'VI'), 'EWCWD': (147398, 'VI'), 'OBCWD': (181575, 'VI'), 'SCCWD': (410043, 'VI')},
    'Electronics and Communication Engineering': {'GNCWD': (25468, 'VI'), 'EWCWD': (177633, 'VI'), 'OBCWD': (188916, 'VI'), 'SCCWD': (310403, 'VIII')},
    'Electronics Engineering (VLSI Design and Technology)': {'GNCWD': (27436, 'VI'), 'OBCWD': (246689, 'VI')},
    'Electrical Engineering': {'GNCWD': (55219, 'VI'), 'EWCWD': (240501, 'VI'), 'OBCWD': (384882, 'VI')},
    'Mechanical Engineering': {'GNCWD': (96162, 'VI'), 'EWCWD': (124364, 'VI'), 'OBCWD': (505244, 'VI'), 'SCCWD': (1315552, 'VI')},
    'Mechanical Engineering with specialization in Automotive Engineering': {'GNCWD': (98028, 'VI'), 'EWCWD': (345801, 'VI'), 'OBCWD': (559592, 'VI')},
    'Engineering Physics': {'GNCWD': (56690, 'VI'), 'OBCWD': (857315, 'VI')},
    'Chemical Engineering': {'GNCWD': (121599, 'VI'), 'EWCWD': (384417, 'VI'), 'OBCWD': (350209, 'VI')},
    'Civil Engineering': {'GNCWD': (113149, 'VI'), 'EWCWD': (342635, 'VI'), 'OBCWD': (688703, 'VI'), 'SCCWD': (1033304, 'VI')},
    'Production & Industrial Engineering': {'GNCWD': (139832, 'VI'), 'OBCWD': (858987, 'VI')},
    'Environmental Engineering': {'GNCWD': (83813, 'VI'), 'OBCWD': (474266, 'VI')},
    'Bio-Technology': {'GNCWD': (128079, 'VI'), 'OBCWD': (932725, 'VI')},
}

DTU_R4_2025_OUTSIDE_CW = {
    'Computer Science and Engineering': {'GNCWO': (768211, 'I'), 'OBCWO': (867962, 'III'), 'SCCWO': (405412, 'V(x)'), 'STCWO': (92242, 'VI')},
    'Information Technology': {'EWCWO': (77000, 'IV'), 'OBCWO': (1059352, 'I')},
    'Information Technology (Cyber Security)': {'GNCWO': (103647, 'III')},
    'Software Engineering': {'OBCWO': (76557, 'IV')},
    'Mathematics and Computing': {'GNCWO': (124111, 'III')},
    'Electronics and Communication Engineering': {'GNCWO': (216593, 'I'), 'EWCWO': (88020, 'IV'), 'SCCWO': (134123, 'VI')},
    'Electrical Engineering': {'GNCWO': (39858, 'IV')},
    'Mechanical Engineering': {'GNCWO': (78306, 'III'), 'OBCWO': (375936, 'IV'), 'SCCWO': (274465, 'VI')},
    'Engineering Physics': {'GNCWO': (168888, 'IV')},
    'Civil Engineering': {'OBCWO': (280603, 'IV')},
}

DTU_R5_2025_DELHI_CW = {
    'Computer Science and Engineering': {'GNCWD': (205133, 'V(v)'), 'EWCWD': (102477, 'VI'), 'OBCWD': (86912, 'VI'), 'SCCWD': (242191, 'VIII'), 'STCWD': (476260, 'VI')},
    'Computer Science and Engineering (Data Science & Analytics)': {'GNCWD': (88380, 'V(vii)'), 'EWCWD': (115837, 'VI'), 'OBCWD': (95366, 'VI'), 'SCCWD': (415350, 'VIII')},
    'Information Technology': {'GNCWD': (362645, 'V(x)'), 'OBCWD': (143686, 'VI')},
    'Information Technology (Cyber Security)': {'GNCWD': (393724, 'V(vii)'), 'EWCWD': (118959, 'VI'), 'SCCWD': (839253, 'VIII')},
    'Software Engineering': {'GNCWD': (1261139, 'V(x)'), 'EWCWD': (137016, 'VI'), 'OBCWD': (160204, 'VI'), 'SCCWD': (394754, 'VIII')},
    'Mathematics and Computing': {'GNCWD': (24086, 'VI'), 'EWCWD': (147398, 'VI'), 'OBCWD': (181575, 'VI'), 'SCCWD': (410043, 'VI')},
    'Electronics and Communication Engineering': {'GNCWD': (40931, 'VI'), 'EWCWD': (177633, 'VI'), 'OBCWD': (188916, 'VI'), 'SCCWD': (310403, 'VIII')},
    'Electronics Engineering (VLSI Design and Technology)': {'GNCWD': (27436, 'VI'), 'OBCWD': (246689, 'VI')},
    'Electrical Engineering': {'GNCWD': (92984, 'VI'), 'EWCWD': (240501, 'VI'), 'OBCWD': (384882, 'VI')},
    'Mechanical Engineering': {'GNCWD': (121599, 'VI'), 'EWCWD': (124364, 'VI'), 'OBCWD': (699925, 'VI'), 'SCCWD': (1315552, 'VI')},
    'Mechanical Engineering with specialization in Automotive Engineering': {'GNCWD': (116177, 'VI'), 'EWCWD': (345801, 'VI'), 'OBCWD': (559592, 'VI')},
    'Engineering Physics': {'GNCWD': (92102, 'VI'), 'OBCWD': (206544, 'VIII')},
    'Chemical Engineering': {'GNCWD': (152965, 'VI'), 'EWCWD': (384417, 'VI'), 'OBCWD': (350209, 'VI')},
    'Civil Engineering': {'GNCWD': (152423, 'VI'), 'EWCWD': (342635, 'VI'), 'OBCWD': (688703, 'VI'), 'SCCWD': (1033304, 'VI')},
    'Production & Industrial Engineering': {'GNCWD': (158992, 'VI'), 'OBCWD': (891801, 'VI')},
    'Environmental Engineering': {'GNCWD': (159833, 'VI'), 'OBCWD': (474266, 'VI')},
    'Bio-Technology': {'GNCWD': (128079, 'VI'), 'OBCWD': (267734, 'VIII')},
}

DTU_R5_2025_OUTSIDE_CW = {
    'Computer Science and Engineering': {'GNCWO': (768211, 'I'), 'OBCWO': (867962, 'III'), 'SCCWO': (405412, 'V(x)'), 'STCWO': (444900, 'VI')},
    'Information Technology': {'EWCWO': (77000, 'IV'), 'OBCWO': (38726, 'IV')},
    'Information Technology (Cyber Security)': {'GNCWO': (103647, 'III')},
    'Software Engineering': {'OBCWO': (76557, 'IV')},
    'Mathematics and Computing': {'GNCWO': (124111, 'III')},
    'Electronics and Communication Engineering': {'GNCWO': (216593, 'I'), 'EWCWO': (88020, 'IV'), 'SCCWO': (134123, 'VI')},
    'Electrical Engineering': {'GNCWO': (39858, 'IV')},
    'Mechanical Engineering': {'GNCWO': (49836, 'IV'), 'OBCWO': (375936, 'IV'), 'SCCWO': (274465, 'VI')},
    'Engineering Physics': {'GNCWO': (168888, 'IV')},
    'Civil Engineering': {'OBCWO': (44636, 'VI')},
}


def load_cw_table(table, year, rnd, source):
    for branch_name, codes in table.items():
        for col, (rank, priority) in codes.items():
            d = decode_code(col)
            add(branch_name, year, rnd, d['category_code'], d['quota_code'], d['region_code'],
                rank, priority, source)


load_cw_table(DTU_R4_2025_DELHI_CW, 2025, 4, 'DTU_R4_2025_Delhi_CW')
load_cw_table(DTU_R4_2025_OUTSIDE_CW, 2025, 4, 'DTU_R4_2025_Outside_CW')
load_cw_table(DTU_R5_2025_DELHI_CW, 2025, 5, 'DTU_R5_2025_Delhi_CW')
load_cw_table(DTU_R5_2025_OUTSIDE_CW, 2025, 5, 'DTU_R5_2025_Outside_CW')

# Kashmiri Migrant quota -- single figure, CSE branch, both rounds (per source)
add('Computer Science and Engineering', 2025, 4, 'GEN', 'KASHMIRI_MIGRANT', None, 285540, source='DTU_R4_2025_KM')
add('Computer Science and Engineering', 2025, 5, 'GEN', 'KASHMIRI_MIGRANT', None, 285540, source='DTU_R5_2025_KM')

fieldnames = ['university', 'branch_code', 'branch_name', 'year', 'round_number',
              'category_code', 'quota_code', 'region_code', 'closing_rank',
              'priority_note', 'source_page_ref']

with open('cutoffs_staging_dtu_2025.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to cutoffs_staging_dtu_2025.csv")

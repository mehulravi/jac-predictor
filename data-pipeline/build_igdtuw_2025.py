"""
build_igdtuw_2025.py — same transposed-table approach as build_igdtuw.py.
2025 adds a new branch, MAC (Mathematics and Computing), as the 9th column.
"""
import csv
from decode import decode_code

BRANCHES = ['CSEAI', 'CSE', 'ECEAI', 'ECE', 'IT', 'AIML', 'MAE', 'DMAM', 'MAC', 'BARCH']
BRANCH_NAMES = {
    'CSEAI': 'Computer Science and Engineering (Artificial Intelligence)',
    'CSE': 'Computer Science and Engineering',
    'ECEAI': 'Electronics and Communication Engineering (Artificial Intelligence)',
    'ECE': 'Electronics and Communication Engineering',
    'IT': 'Information Technology',
    'AIML': 'Artificial Intelligence and Machine Learning',
    'MAE': 'Mechanical and Automation Engineering',
    'DMAM': 'Dual Degree B.Tech-MBA (Mechanical and Automation Engineering)',
    'MAC': 'Mathematics and Computing',
    'BARCH': 'Bachelor of Architecture (Paper 2)',
}

rows = []


def add(code_row, branch, year, rnd, rank, priority=None, source=''):
    if rank is None:
        return
    if code_row == 'SG':
        category_code, quota_code, region_code = 'GEN', 'SIKKIM_GOA', None
    elif code_row == 'KM':
        category_code, quota_code, region_code = 'GEN', 'KASHMIRI_MIGRANT', None
    else:
        d = decode_code(code_row)
        category_code, quota_code, region_code = d['category_code'], d['quota_code'], d['region_code']
    rows.append({
        'university': 'IGDTUW', 'branch_code': branch, 'branch_name': BRANCH_NAMES[branch],
        'year': year, 'round_number': rnd, 'category_code': category_code,
        'quota_code': quota_code, 'region_code': region_code,
        'closing_rank': rank, 'priority_note': priority, 'source_page_ref': source,
    })


def load_table(table, year, rnd, source):
    for code_row, vals in table.items():
        for branch, v in zip(BRANCHES, vals):
            if v is None:
                continue
            rank, priority = v if isinstance(v, tuple) else (v, None)
            add(code_row, branch, year, rnd, rank, priority, source)


IGDTUW_R4_2025_DELHI = {
    'GNGND': [39100, 45659, 67897, 70912, 58837, 55305, 82767, 88223, 63515, 2370],
    'GNCWD': [(57247, 'VI'), (83075, 'VI'), (141971, 'VI'), (122652, 'VI'), (106260, 'VI'),
              (106901, 'VI'), (188819, 'VI'), (189095, 'VI'), (121378, 'VI'), (5547, 'VI')],
    'GNPDD': [433013, 313995, 1070615, 918000, 946450, 518972, None, None, 758044, 5674],
    'SCGND': [392640, 369691, 615100, 584896, 494818, 458845, 727646, 761432, 563697, 21414],
    'STGND': [1183864, 969509, None, None, None, None, None, None, None, 17580],
    'OBGND': [184818, 199828, 317456, 329695, 259799, 274831, 388011, 428213, 305126, 17341],
    'OBCWD': [(324939, 'VI'), (371303, 'VI'), (423703, 'VI'), (448138, 'VI'), (396019, 'VI'),
              (377508, 'VI'), (491287, 'VI'), None, (479854, 'VI'), None],
    'EWGND': [90813, 117689, 183883, 178912, 151085, 135852, 230706, 236219, 161353, 26840],
    'EWCWD': [(305236, 'VI'), (297111, 'VI'), (556266, 'VI'), None, None,
              (638944, 'VI'), (273427, 'VI'), None, None, None],
    'SG': [43094, 47534, 79024, 81599, 66195, 64133, 100050, 116920, 79298, None],
    'KM': [None, 206575, None, None, None, None, None, None, None, None],
}

IGDTUW_R4_2025_OUTSIDE = {
    'GNGNO': [19657, 17974, 24591, 23400, 22432, 21745, 27044, 29448, 23380, 1014],
    'GNCWO': [(99379, 'IV'), (162681, 'IV'), (170117, 'V(vii)'), None, None, None, None, None, None, (5527, 'VI')],
    'GNPDO': [156220, 130295, None, 263399, 183061, None, None, None, None, None],
    'SCGNO': [171001, 159820, 186518, 178082, 173161, 181695, 189287, 189612, 187743, None],
    'SCCWO': [None, None, None, None, (181214, 'VI'), None, None, None, None, None],
    'STGNO': [240177, 183056, 347061, 335266, 298847, 301035, 363156, None, 356418, 3002],
    'OBGNO': [41487, 40534, 51611, 50618, 48908, 48607, 55610, 55961, 50763, 3120],
    'OBCWO': [(373417, 'IV'), None, None, None, (919670, 'V(x)'), (56664, 'VI'), None, None, None, None],
    'OBPDO': [None, 877504, 696244, None, None, None, None, None, None, None],
    'EWGNO': [29186, 26656, 36953, 32978, 30009, 30639, 37700, None, 31319, None],
    'EWCWO': [None, None, None, None, None, (116909, 'VI'), None, None, None, None],
}

IGDTUW_R5_2025_DELHI = {
    'GNGND': [44405, 50687, 75759, 79574, 64223, 64133, 92818, 94672, 69001, 2977],
    'GNCWD': [(73137, 'VI'), (103166, 'VI'), (163090, 'VI'), (141971, 'VI'), (121378, 'VI'),
              (106901, 'VI'), (188819, 'VI'), (189095, 'VI'), (132749, 'VI'), (5547, 'VI')],
    'GNPDD': [433013, 313995, 1070615, 1360126, 946450, 518972, None, None, 758044, 5674],
    'SCGND': [413693, 399917, 698598, 597563, 516592, 470209, 820634, 856293, 617454, 21675],
    'STGND': [1183864, 969509, None, None, None, None, None, None, None, 17580],
    'OBGND': [186225, 204747, 339542, 346713, 270817, 280051, 425801, 450146, 306445, 18619],
    'OBCWD': [(324939, 'VI'), (371303, 'VI'), (423703, 'VI'), (448138, 'VI'), (396019, 'VI'),
              (377508, 'VI'), (491287, 'VI'), None, (479854, 'VI'), None],
    'EWGND': [90958, 118163, 183883, 192517, 151085, 135852, 244309, 245925, 163983, 18377],
    'EWCWD': [(305236, 'VI'), (297111, 'VI'), (556266, 'VI'), None, None,
              (638944, 'VI'), (273427, 'VI'), None, None, None],
    'SG': [47534, 56996, 80409, 87211, 66195, 75091, 116920, 137809, 79298, None],
    'KM': [None, 206575, None, None, None, None, None, None, None, None],
}

IGDTUW_R5_2025_OUTSIDE = {
    'GNGNO': [23158, 20667, 27368, 27449, 25486, 25326, 30228, 31577, 26176, 1129],
    'GNCWO': [(99379, 'IV'), (162681, 'IV'), (170117, 'V(vii)'), None, None, None, None, None, None, (5527, 'VI')],
    'GNPDO': [156220, 130295, None, 263399, 183061, None, None, None, None, None],
    'SCGNO': [171651, 159820, 190655, 189771, 181040, 185443, 193338, 206949, 190705, None],
    'SCCWO': [None, None, None, None, (181214, 'VI'), None, None, None, None, None],
    'STGNO': [240177, 298847, 362325, 237746, 339001, 301035, 385313, None, 356418, 8691],
    'OBGNO': [48607, 44123, 55626, 53744, 50746, 51611, 59229, 57384, 53447, 3307],
    'OBCWO': [(373417, 'IV'), None, None, None, (919670, 'V(x)'), (68346, 'VI'), None, None, None, None],
    'OBPDO': [None, 877504, 696244, None, None, None, None, None, None, None],
    'EWGNO': [32454, 29387, 38849, 36953, 32978, 33019, 40700, None, 35532, None],
    'EWCWO': [None, None, None, None, None, (116909, 'VI'), None, None, None, None],
}

load_table(IGDTUW_R4_2025_DELHI, 2025, 4, 'IGDTUW_R4_2025_Delhi')
load_table(IGDTUW_R4_2025_OUTSIDE, 2025, 4, 'IGDTUW_R4_2025_Outside')
load_table(IGDTUW_R5_2025_DELHI, 2025, 5, 'IGDTUW_R5_2025_Delhi')
load_table(IGDTUW_R5_2025_OUTSIDE, 2025, 5, 'IGDTUW_R5_2025_Outside')

fieldnames = ['university', 'branch_code', 'branch_name', 'year', 'round_number',
              'category_code', 'quota_code', 'region_code', 'closing_rank',
              'priority_note', 'source_page_ref']

with open('cutoffs_staging_igdtuw_2025.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to cutoffs_staging_igdtuw_2025.csv")

"""
decode.py — decodes JAC/DTU/NSUT/IGDTUW/IIITD category codes into
(category, quota, region) triples.

Pattern:  [CATEGORY: 2 chars] + [QUOTA: 2 chars] + [REGION: 1 char, optional]

CATEGORY  GN=General EW=EWS OB=OBC SC=SC ST=ST
QUOTA     GN=General/Gender-Neutral  GL=Girls-only  CW=Defence(priority)
          PD=PwD  SG=Sikkim/Goa domicile  KM=Kashmiri Migrant (no region letter)
REGION    D=Delhi   O=Outside Delhi
"""

CATEGORY_MAP = {'GN': 'GEN', 'EW': 'EWS', 'OB': 'OBC', 'SC': 'SC', 'ST': 'ST'}
QUOTA_MAP = {
    'GN': 'GENERAL', 'GL': 'GIRLS', 'CW': 'DEFENCE_CW',
    'PD': 'PWD', 'SG': 'SIKKIM_GOA', 'KM': 'KASHMIRI_MIGRANT',
}
REGION_MAP = {'D': 'DELHI', 'O': 'OUTSIDE_DELHI'}


def decode_code(code: str):
    """Returns dict: category_code, quota_code, region_code (region may be None)."""
    code = code.strip().upper()
    cat_part = code[:2]
    rest = code[2:]

    if cat_part not in CATEGORY_MAP:
        raise ValueError(f"Unknown category prefix in code: {code}")
    category = CATEGORY_MAP[cat_part]

    if rest == 'KM':
        return {'category_code': category, 'quota_code': 'KASHMIRI_MIGRANT', 'region_code': None}

    if len(rest) == 3:
        quota_part, region_part = rest[:2], rest[2]
        if quota_part not in QUOTA_MAP:
            raise ValueError(f"Unknown quota part in code: {code}")
        if region_part not in REGION_MAP:
            raise ValueError(f"Unknown region part in code: {code}")
        return {
            'category_code': category,
            'quota_code': QUOTA_MAP[quota_part],
            'region_code': REGION_MAP[region_part],
        }

    raise ValueError(f"Could not decode code: {code}")


if __name__ == "__main__":
    tests = ["GNGND", "GNGLD", "OBCWO", "EWGLD", "GNKM", "SCPDD", "GNSGD"]
    for t in tests:
        print(t, "->", decode_code(t))

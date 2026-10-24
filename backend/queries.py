"""
queries.py — the actual SQL. Kept separate from main.py so the queries can
be read, tested, and explained on their own (this is the file worth walking
an interviewer through).
"""

TREND_SQL = """
-- shows how one branch+category's cutoff moved across rounds (for a trend chart)
SELECT ro.year, ro.round_number, c.closing_rank
FROM cutoffs c
JOIN branches b     ON c.branch_id = b.branch_id
JOIN universities u ON b.university_id = u.university_id
JOIN categories cat ON c.category_id = cat.category_id
JOIN quota_types q  ON c.quota_id = q.quota_id
JOIN gender_pools g ON c.gender_pool_id = g.gender_pool_id
JOIN home_regions r ON c.region_id = r.region_id
JOIN rounds ro       ON c.round_id = ro.round_id
WHERE u.short_code = :university
  AND b.branch_code = :branch_code
  AND cat.category_code = :category
  AND q.quota_code = :quota
  AND g.pool_code = :gender
  AND r.region_code = COALESCE(:region, 'NOT_APPLICABLE')
  AND c.rank_type = :rank_type
  AND c.with_bonus = :with_bonus
ORDER BY ro.year, ro.round_number
"""

META_UNIVERSITIES_SQL = "SELECT university_id, short_code, full_name, location_city, admits_gender FROM universities"

META_BRANCHES_SQL = """
SELECT b.branch_id, u.short_code AS university, b.branch_code, b.branch_name, cm.campus_name
FROM branches b
JOIN universities u ON b.university_id = u.university_id
LEFT JOIN campuses cm ON b.campus_id = cm.campus_id
WHERE (:university IS NULL OR u.short_code = :university)
ORDER BY u.short_code, b.branch_code
"""

META_ROUNDS_SQL = "SELECT year, round_number FROM rounds ORDER BY year DESC, round_number DESC"

# ---------------------------------------------------------------------
# Multi-year predictor: compares the SAME round number across every year
# that has data for a branch+category+quota+gender+region combination,
# rather than trusting a single year's snapshot. One row per branch,
# with each year's closing rank as its own column.
# ---------------------------------------------------------------------
PREDICT_MULTI_YEAR_SQL = """
SELECT
    u.short_code       AS university,
    u.full_name        AS university_full_name,
    b.branch_code,
    b.branch_name,
    cm.campus_name,
    ro.year,
    c.closing_rank,
    c.priority_note
FROM cutoffs c
JOIN branches b      ON c.branch_id = b.branch_id
JOIN universities u  ON b.university_id = u.university_id
LEFT JOIN campuses cm ON b.campus_id = cm.campus_id
JOIN categories cat  ON c.category_id = cat.category_id
JOIN quota_types q   ON c.quota_id = q.quota_id
JOIN gender_pools g  ON c.gender_pool_id = g.gender_pool_id
JOIN home_regions r  ON c.region_id = r.region_id
JOIN rounds ro        ON c.round_id = ro.round_id
WHERE cat.category_code = :category
  AND q.quota_code = :quota
  AND g.pool_code IN (:pool_1, :pool_2)
  AND (:applicant_gender = 'FEMALE' OR u.admits_gender = 'ALL')
  AND r.region_code = COALESCE(:region, 'NOT_APPLICABLE')
  AND ro.round_number = :round_number
  AND c.rank_type = :rank_type
  AND c.with_bonus = :with_bonus
ORDER BY b.branch_id, ro.year
"""

-- schema.sql: SQLite schema for the JAC Predictor.
-- Table and column names are exactly the ones backend/queries.py reads.

PRAGMA foreign_keys = ON;

CREATE TABLE universities (
    university_id  INTEGER PRIMARY KEY,
    short_code     TEXT NOT NULL UNIQUE,          -- DTU, NSUT, IIITD, IGDTUW
    full_name      TEXT NOT NULL,
    location_city  TEXT,
    admits_gender  TEXT NOT NULL CHECK (admits_gender IN ('ALL', 'FEMALE_ONLY'))
);

CREATE TABLE campuses (
    campus_id    INTEGER PRIMARY KEY,
    campus_name  TEXT NOT NULL UNIQUE             -- NSUT East / West
);

CREATE TABLE branches (
    branch_id      INTEGER PRIMARY KEY,
    university_id  INTEGER NOT NULL REFERENCES universities (university_id),
    campus_id      INTEGER REFERENCES campuses (campus_id),   -- NULL = main / only campus
    branch_code    TEXT NOT NULL,
    branch_name    TEXT NOT NULL
);
CREATE UNIQUE INDEX ux_branches ON branches (university_id, branch_code, IFNULL(campus_id, 0));

CREATE TABLE categories (
    category_id    INTEGER PRIMARY KEY,
    category_code  TEXT NOT NULL UNIQUE,          -- GEN, EWS, OBC, SC, ST
    category_name  TEXT
);

CREATE TABLE quota_types (
    quota_id    INTEGER PRIMARY KEY,
    quota_code  TEXT NOT NULL UNIQUE,             -- GENERAL, PWD, DEFENCE_CW, KASHMIRI_MIGRANT, SIKKIM_GOA
    quota_name  TEXT
);

CREATE TABLE gender_pools (
    gender_pool_id  INTEGER PRIMARY KEY,
    pool_code       TEXT NOT NULL UNIQUE,         -- GN (gender-neutral), GIRL (girls-only seats)
    pool_name       TEXT
);

CREATE TABLE home_regions (
    region_id    INTEGER PRIMARY KEY,
    region_code  TEXT NOT NULL UNIQUE,            -- DELHI, OUTSIDE_DELHI, NOT_APPLICABLE
    region_name  TEXT
);

CREATE TABLE rounds (
    round_id      INTEGER PRIMARY KEY,
    year          INTEGER NOT NULL,
    round_number  INTEGER NOT NULL,
    UNIQUE (year, round_number)
);

CREATE TABLE cutoffs (
    cutoff_id       INTEGER PRIMARY KEY,
    branch_id       INTEGER NOT NULL REFERENCES branches (branch_id),
    category_id     INTEGER NOT NULL REFERENCES categories (category_id),
    quota_id        INTEGER NOT NULL REFERENCES quota_types (quota_id),
    gender_pool_id  INTEGER NOT NULL REFERENCES gender_pools (gender_pool_id),
    region_id       INTEGER NOT NULL REFERENCES home_regions (region_id),
    round_id        INTEGER NOT NULL REFERENCES rounds (round_id),
    rank_type       TEXT NOT NULL CHECK (rank_type IN ('JEE_CRL', 'IIITD_RANK')),
    with_bonus      INTEGER NOT NULL DEFAULT 0 CHECK (with_bonus IN (0, 1)),
    closing_rank    INTEGER NOT NULL CHECK (closing_rank > 0),
    priority_note   TEXT,
    source_page_ref TEXT
);

-- Serves /api/predict: filters by round + category + quota + region + pool + rank type + bonus.
CREATE INDEX idx_cutoffs_predict
    ON cutoffs (round_id, category_id, quota_id, region_id, gender_pool_id, rank_type, with_bonus);

-- Serves /api/trend and the branch join.
CREATE INDEX idx_cutoffs_branch
    ON cutoffs (branch_id, category_id, quota_id, gender_pool_id, region_id);

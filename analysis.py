import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from helpers import get_matches, clean_school_data, plot_average_rates, plot_rates

# WashU = 'Washington University in St Louis'
# UNITID = 179867
'''
Plan:
Compare low-income enrollment or completion at Wash U vs. similar schools based
on admissions, SAT/ACT scores, something else-- Wash U considers self elite but
I know low-income enrollment is a problem. Match with other schools (clustering
on SAT/ACT scores, admission rates, tuition). Compare completion rates trends.
If leaders: use to our advantage! If not, what can we learn from others?

Filter to get only schools with same rates in 1999/2000 whatever earliest year is.
See if others are trending up/down.

Brainstorm possible predictors and try to fit a linear regression. Or advise
some qualitative research/domain knowledge to identify possible predictors.

Findings:
At Wash U, looks like overall completion rates are increasing over time, low income
were trailing high income but look to be catching up.
'''

query_schools='''
SELECT  INSTNM,
        UNITID,
        UGDS, -- size of undergrad student body
        ADM_RATE,
        SATVRMID,
        SATMTMID,
        SATWRMID,
        COSTT4_A
FROM Scorecard
WHERE Year=2013
AND ADM_RATE IS NOT NULL
AND ADM_RATE != 0.0
AND PREDDEG="Predominantly bachelor's-degree granting";
'''

query_perf='''
SELECT  UNITID
        , INSTNM
        , Year
        , PCTPELL -- pct of student body with Pell grants
        , COMP_ORIG_YR4_RT -- overall 4 yr completion rate
        , HI_INC_COMP_ORIG_YR4_RT -- 4 yr completion rate for low income students
        , LO_INC_COMP_ORIG_YR4_RT -- high income students
        , OVERALL_YR4_N
        , HI_INC_YR4_N
        , LO_INC_YR4_N
FROM Scorecard
WHERE UNITID in ({0})
ORDER BY Year;
'''

query_perf_wu='''
SELECT  UNITID,
        INSTNM,
        Year,
        PCTPELL, -- pct of student body with Pell grants
        COMP_ORIG_YR4_RT, -- overall 4 yr completion rate
        LO_INC_COMP_ORIG_YR4_RT, -- 4 yr completion rate for low income students
        HI_INC_COMP_ORIG_YR4_RT
FROM Scorecard
WHERE UNITID=179867 AND Year > 1999
ORDER BY Year;
'''

query_props='''
SELECT OVERALL_YR4_N
       , HI_INC_YR4_N
       , LO_INC_YR4_N
       , LO_INC_COMP_ORIG_YR4_RT
       , HI_INC_COMP_ORIG_YR4_RT
FROM Scorecard
WHERE UNITID=179867 AND Year=2011
;
'''


if __name__ == '__main__':
    conn = sqlite3.connect('college.sqlite')

    # wu = pd.read_sql(query_perf_wu, conn)

    all_schools = pd.read_sql(query_schools, conn)
    matches = get_matches(all_schools, 'kmeans')
    ids = matches['unitid'].tolist()
    print len(ids)
    del all_schools #try to free up memory
    del matches
    ## Build SQL query to get all match schools
    placeholder = '?' # For SQLite. See DBAPI paramstyle.
    placeholders = ', '.join(placeholder for _ in ids)
    match_school_info = pd.read_sql(query_perf.format(placeholders), conn, params=ids)
    clean_matches = clean_school_data(match_school_info, complete=True)
    plot_average_rates(clean_matches, fname='averages.png')

    ## 2011 rates for z-test
    #wu_2011=pd.read_sql(query_props, conn)

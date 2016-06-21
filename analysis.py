import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from helpers import get_matches, plot_dendrogram, plot_rates

# WashU = 'Washington University in St Louis'
# UNITID = 179867
'''
Compare low-income enrollment or completion at Wash U vs. similar schools based
on admissions, SAT/ACT scores, something else-- Wash U considers self elite but
I know low-income enrollment is a problem. Match with other schools (clustering?)
on SAT/ACT scores, admission rates, tuition?
'''

#going to return a lot of schools to then cluster and find those similar to WashU:
query_school_matches='''
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
SELECT  UNITID,
        INSTNM,
        Year,
        PCTPELL, -- pct of student body with Pell grants
        COMP_ORIG_YR4_RT, -- overall 4 yr completion rate
        C150_4_WHITE, -- 4 yr completion rate for whites
        C150_4_BLACK,
        C150_4_HISP,
        LO_INC_COMP_ORIG_YR4_RT, -- 4 yr completion rate for low income students
        HI_INC_COMP_ORIG_YR4_RT -- high income students
FROM Scorecard
WHERE UNITID in {0} -- add subquery to get for all ~150 match schools
ORDER BY Year;

'''

query_perf_inc='''
SELECT  COMP_ORIG_YR4_RT,
        LO_INC_COMP_ORIG_YR4_RT,
        -- MD_INC_COMP_ORIG_YR4_RT, -- privacy suppressed in almost every case
        HI_INC_COMP_ORIG_YR4_RT,
        Year
FROM Scorecard
WHERE UNITID=179867 AND Year > 1999
ORDER BY Year;
'''
# raw numbers (denoms):
# OVERALL_YR4_N
# LO_INC_YR4_N
# MD_INC_YR4_N
# HI_INC_YR4_N

'''
Plan:
Build a large pd dataframe with above rows for all schools in Wash U's cohort.
identify those who are doing better (over time)

Wash U: looks like overall completion rates are increasing over time, low income
were trailing high income but look to be catching up.

Compare to other schools and figure out if we are doing comparatively better/worse.
If leaders: use to our advantage! If not, what can we learn from others?
'''


if __name__ == '__main__':
    conn = sqlite3.connect('college.sqlite') #must be in home directory
    all_schools = pd.read_sql(query_school_matches, conn)
    # matches = get_matches(all_schools)
    # ids = matches['UNITID'].tolist()
    #
    # placeholder= '?' # For SQLite. See DBAPI paramstyle.
    # placeholders= ', '.join(placeholder for _ in ids)
    # c = conn.cursor()
    # c.execute(query_perf.format(placeholders), ids) ## see if this works?
    ## pandas alternative:
    #match_school_info = pd.read_sql(query_perf.format(placeholders), params=ids)

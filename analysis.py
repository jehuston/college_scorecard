import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from helpers import get_matches, plot_dendrogram, plot_rates

# WashU = 'Washington University in St Louis'
# UNITID = 179867
'''
Compare low-income enrollment or completion at Wash U vs. similar schools based
on admissions, SAT/ACT scores, something else-- Wash U considers self elite but
I know low-income enrollment is a problem. Match with other schools (clustering?)
on SAT/ACT scores, admission rates, tuition. Compare mean completion rates.

Filter to get only schools with same rates in 1999/2000 whatever earliest year is.
See if others are trending up/down.

Brainstorm possible predictors and try to fit a linear regression. Or advise
some qualitative research/domain knowledge to identify possible predictors.
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
WHERE UNITID in ({0})
/*WHERE UNITID in (110404, 112260, 115409, 121345, 123165, 123961, 130697, 130794,
                139658, 144050, 147767, 161004, 162928, 164465, 164924, 166027,
                166683, 167358, 168148, 168218, 168342, 173258, 179867, 182670,
                186131, 189097, 190150, 190372, 190415, 191515, 193900, 197133,
                197221, 198419, 204501, 211440, 212911, 215062, 216287, 217156,
                221999, 227757, 230959, 234207, 243744, 441982)*/
ORDER BY Year;

'''

query_perf_wu='''
SELECT  UNITID,
        INSTNM,
        Year,
        PCTPELL, -- pct of student body with Pell grants
        COMP_ORIG_YR4_RT, -- overall 4 yr completion rate
        C150_4_WHITE, -- 4 yr completion rate for whites
        C150_4_BLACK,
        C150_4_HISP,
        LO_INC_COMP_ORIG_YR4_RT, -- 4 yr completion rate for low income students
        HI_INC_COMP_ORIG_YR4_RT
FROM Scorecard
WHERE UNITID=179867 AND Year > 1999
ORDER BY Year;
'''

query_raw_nums='''
SELECT OVERALL_YR4_N
       , HI_INC_YR4_N
       , MD_INC_YR4_N
       , LO_INC_YR4_N
FROM Scorecard
WHERE UNITID=179867 AND Year > 1999
ORDER BY Year;
'''
# raw numbers (denoms):  --> try to impute Mid income? Check denoms add up
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
    conn = sqlite3.connect('college.sqlite')

    wu = pd.read_sql(query_perf_wu, conn)

    all_schools = pd.read_sql(query_school_matches, conn)
    matches = get_matches(all_schools, 'kmeans')
    ids = matches['unitid'].tolist()
    print len(ids)
    ## Build SQL query to get all match schools
    placeholder = '?' # For SQLite. See DBAPI paramstyle.
    placeholders = ', '.join(placeholder for _ in ids)
    # pandas alternative:
    match_school_info = pd.read_sql(query_perf.format(placeholders), conn, params=ids)
    #average_matches = match_school_info.groupby('Year')[['HI_INC_COMP_ORIG_YR4_RT', 'LO_INC_COMP_ORIG_YR4_RT', 'COMP_ORIG_YR4_RT']].aggregate(np.sum)
    #print average_matches

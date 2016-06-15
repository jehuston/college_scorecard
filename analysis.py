import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


conn = sqlite3.connect('college.sqlite') #whatever database name is
c = conn.cursor()


# WashU = 'Washington University in St Louis'
# UNITID = 179867

'''
Look at ACT/SAT midpoint scores
'''
query_scores='''
SELECT  SATVRMID as SAT_verbal,
        SATMTMID as SAT_math,
        SATWRMID as SAT_writing,
        ACTCMMID as ACT_cum,
        ACTENMID as ACT_eng,
        ACTMTMID as ACT_math,
        ACTWRMID as ACT_writing,
        SAT_AVG as SAT_equiv
FROM Scorecard
WHERE UNITID=179867
AND Year=2013;
'''

query_tuition='''
SELECT INSTNM, COSTT4_A
FROM Scorecard
WHERE Year =2013
AND UNITID=179867;
'''

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
SELECT  PCTPELL,
        C150_4_WHITE,
        C150_4_BLACK,
        C150_4_HISP,
        COMP_ORIG_YR4_RT,
        LO_INC_COMP_ORIG_YR4_RT,
        MD_INC_COMP_ORIG_YR4_RT,
        HI_INC_COMP_ORIG_YR4_RT,
        Year
FROM Scorecard
WHERE UNITID=179867
GROUP BY Year;

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
# Get their UNITIDs, track other metrics through years.
# Things I want to compare:
# PCTPELL - students with Pell grants
# C150_4_WHITE - completion rates for whites
# C150_4_BLACK - black
# C150_4_HISP - hispanic
# C150_4_ASIAN - asian
# C150_4_AIAN - american indian/alaskan native
# C150_4_NHPI - native hawaiian/pacific islander
#
# 4 year completions:
# COMP_ORIG_YR4_RT - % completed within 4 yrs at orig inst.
# LO_INC_COMP_ORIG_YR4_RT - % low income completed w/in 4 yrs
# MD_INC_COMP_ORIG_YR4_RT - % middle income completed w/in 4 yrs
# HI_INC_COMP_ORIG_YR4_RT - % high income completed w/in 4 yrs
# raw numbers (denoms):
# OVERALL_YR4_N
# LO_INC_YR4_N
# MD_INC_YR4_N
# HI_INC_YR4_N

# build a large pd dataframe with above rows for all schools in Wash U's cohort.
# identify those who are doing better (over time)

# looks like overall completion rates are increasing over time, low income
# were trailing high income but look to be catching up. Compare to other
# schools and figure out if we are doing comparatively better/worse.
# If leaders: use to our advantage! If not, what can we learn from others?

# result = c.execute(query_perf_inc)
# #print [r for r in result]
# answer = ["{0}: Overall {1}, Low {2}, High {3}".format(r[3], r[0], r[1], r[2]) for r in result]
# print "\n".join(answer)

# data = pd.read_sql(query_perf_inc, conn)
# data.rename(columns = {'COMP_ORIG_YR4_RT' : 'all_students_rate', 'LO_INC_COMP_ORIG_YR4_RT':\
#     'low_income_rate', 'HI_INC_COMP_ORIG_YR4_RT' : 'high_income_rate', 'Year' :'year'}, inplace=True)
# data.loc[data['low_income_rate'] == 'PrivacySuppressed', 'low_income_rate'] = None
# data.loc[data['high_income_rate'] == 'PrivacySuppressed', 'high_income_rate'] = None
# print data.head()

'''
Looking at plot of rates of income levels across time;
possible that trend of high income students outperforming low income students
in 4-year completion rates might be lessening or reversing but need to keep watching.
'''
all_schools = pd.read_sql(query_school_matches, conn)

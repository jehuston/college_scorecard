import sqlite3

conn = sqlite3.connect('college.sqlite') #whatever database name is
c = conn.cursor()


# WashU = 'Washington University in St Louis'
# UNITID = 179867

'''
Some questions:
Compare social sciences and some other degrees @ WashU.
'''
query_pctss='''
SELECT PCIP45, Year
FROM Scorecard
WHERE UNITID = 179867;
'''

'''
Look at change in ACT/SAT midpoint scores or percentiles over time
CIP45BACHL = Bachelor's degree in Social Sciences (Y/N), PCIP45 = Percentage of SS
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
AND PREDDEG="Predominantly bachelor's-degree granting"
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
        MD_INC_COMP_ORIG_YR4_RT,
        HI_INC_COMP_ORIG_YR4_RT,
        Year
FROM Scorecard
WHERE UNITID=179867
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

result = c.execute(query_perf_inc)
#print [r for r in result]
print ["{0}: Overall {1}, Low {2}, Mid {3}, High {4}\n".format(r[4], r[0], r[1], r[2], r[3]) for r in result]
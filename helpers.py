import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from sklearn.preprocessing import scale
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram, cut_tree

def clean_school_data(df, complete=False, impute=False):
    '''
    Impute missing values in schools data frame
    '''
    dfc = df.copy()
    dfc.columns = map(str.lower, df.columns)
    if complete:
        dfc.loc[dfc['lo_inc_comp_orig_yr4_rt'] == 'PrivacySuppressed', 'lo_inc_comp_orig_yr4_rt'] = None
        dfc.loc[dfc['hi_inc_comp_orig_yr4_rt'] == 'PrivacySuppressed', 'hi_inc_comp_orig_yr4_rt'] = None

    if impute:
        dfc = dfc.fillna(dfc.mean()) # don't impute for plotting!
    return dfc

def filter_dataframe(df, col):
    '''
    Filter dataframe based on column to only rows where column is not null
    '''
    dfc = df.copy()
    dfc = dfc[dfc[col].notnull()]
    dfc.loc[ :, col] = dfc[col].astype(float)
    return dfc

def group_dataframe():
    #? worth it
    pass


def make_kmeans(df): # SO much better!
    '''
    Given dataframe of schools and chosen attributes, use KMeans clustering to find
    ideal number of clusters and by extension, similar schools.
    '''
    vectors = df.iloc[:, 2:].values #skip columns with id #s, school name
    vectors = scale(vectors)
    clusters = range(20, 100, 10)
    scores = np.zeros(len(clusters))
    for i, k in enumerate(clusters):
        km = KMeans(n_clusters=k)
        km.fit(vectors)
        scores[i] = silhouette_score(vectors, km.labels_)

    best_k = clusters[np.argmax(scores)]
    km = KMeans(n_clusters=best_k)
    km.fit(vectors)
    labels = km.labels_
    return best_k, labels

def make_hier_clusters(df, n):
    '''
    Given dataframe of schools and attributes, use hierarchical clustering to
    find most similar schools.
    '''
    vectors = df.iloc[:, 2:].values
    vectors = scale(vectors)
    dist_matrix = squareform(pdist(vectors, metric='cosine'))
    link_matrix = linkage(dist_matrix, method='average')
    tree = cut_tree(link_matrix, n)
    return link_matrix, tree


def plot_dendrogram(matr, fname=None):
    '''
    Given linkage matrix of schools, plot dendrogram
    '''
    plt.figure()
    dendrogram(matr)
    if fname != None:
        plt.savefig(fname)

def plot_rates(df, cols, fname=None):
    '''
    Given dataframe with rates across income levels, plot rates over years
    (in 'year' column)
    '''
    for col in cols:
        lab = " ".join(col.split('_')[:2])
        plt.plot(df['year'], df[col], '-o', label=lab)
    plt.xlabel('Year')
    plt.ylabel('4-year completion rate')
    plt.title('Four year completion rates across income levels')
    plt.legend(loc=4)

    if fname != None:
        plt.savefig(fname)

def get_matches(df, method, n=20, ID=179867):
    clean = clean_school_data(df, impute=True)

    if method == 'hier':
        _, labels = make_hier_clusters(clean, n)

    elif method == 'kmeans':
        _, labels = make_kmeans(clean)

    idx = clean[clean['unitid'] == ID].index[0]
    match_idx = np.where(labels == labels[idx])[0] # where returns a tuple
    match_df = clean.iloc[match_idx, :]
    return match_df

def plot_average_rates(df):
    df_hi = filter_dataframe(df, 'hi_inc_comp_orig_yr4_rt')
    df_low = filter_dataframe(df, 'lo_inc_comp_orig_yr4_rt')
    high_incomes = df_hi.groupby('year')['hi_inc_comp_orig_yr4_rt'].mean()
    low_incomes = df_low.groupby('year')['lo_inc_comp_orig_yr4_rt'].mean()
    plt.plot(high_incomes, '-o', label='High income')
    plt.plot(low_incomes, '-o', label='Low income')
    plt.xlabel('Year')
    plt.ylabel('4-year completion rate')
    plt.title('Average four year completion rates across similar schools')
    plt.legend(loc=4)  

## imputing n:
# wu['sum_inc_levels'] = wu[['HI_INC_YR4_N', 'MD_INC_YR4_N', 'LO_INC_YR4_N']].sum(axis = 1, skipna=True)

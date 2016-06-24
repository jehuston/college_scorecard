import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import scipy.stats as scs
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
        plt.plot(df['year'], df[col], '-o', label='WashU') #lab)
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

def plot_average_line(df, rt_col, n_col, label):
    '''
    compute and plot 1 group's national average
    '''
    df = filter_dataframe(df, rt_col)
    df['num'] = df[rt_col] * df[n_col]
    grouped = df.groupby('year').aggregate(sum)
    grouped['avg_rate'] = grouped['num'] / grouped[n_col]
    plt.plot(grouped['avg_rate'], '-o', label=label)


def plot_average_rates(df, fname=None):
    '''
    Compare national average 4-year completion rates for low and high income students.
    '''
    # prep data
    df_hi = filter_dataframe(df, 'hi_inc_comp_orig_yr4_rt')
    df_low = filter_dataframe(df, 'lo_inc_comp_orig_yr4_rt')
    df_low['lo_inc_yr4_n'] = df_low['lo_inc_yr4_n'].astype('int')
    df_hi['hi_inc_yr4_n'] = df_hi['hi_inc_yr4_n'].astype('int')

    plot_average_line(df_hi, 'hi_inc_comp_orig_yr4_rt', 'hi_inc_yr4_n', 'High income')
    plot_average_line(df_low, 'lo_inc_comp_orig_yr4_rt', 'lo_inc_yr4_n', 'Low income')
    plt.xlabel('Year')
    plt.ylabel('4-year completion rate')
    plt.title('Average four year completion rate across similar schools')
    plt.legend(loc=4)

    if fname != None:
        plt.savefig(fname)

def find_z_test(p1, p2, n1, n2):
    '''
    Conduct z-test for 2 proportions, return p-value.
    null : p1 - p2 = 0
    alt: p1 - p2 != 0
    '''
    pooled_p = (p1*n1 + p2*n2)/(n1 + n2)
    SE = np.sqrt(pooled_p*(1-pooled_p)*((1./n1) + (1./n2)))
    z = (p1 - p2)/SE
    p = (1 - scs.norm.cdf(abs(z)))*2
    return z, p

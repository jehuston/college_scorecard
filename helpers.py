import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram, cut_tree

def clean_school_data(df, complete=False):
    '''
    Impute missing values in schools data frame
    '''
    if complete:
        df.rename(columns = {'COMP_ORIG_YR4_RT' : 'all_students_rate',\
                    'LO_INC_COMP_ORIG_YR4_RT': 'low_income_rate', \
                    'HI_INC_COMP_ORIG_YR4_RT' : 'high_income_rate', \
                    'Year' :'year'}, inplace=True)
        df.loc[df['low_income_rate'] == 'PrivacySuppressed', 'low_income_rate'] = None
        df.loc[df['high_income_rate'] == 'PrivacySuppressed', 'high_income_rate'] = None

    df = df.fillna(df.mean())
    return df

def plot_rates(df, cols):
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

def make_kmeans(df):
    '''
    Given dataframe of schools and chosen attributes, use KMeans clustering to find
    ideal number of clusters and by extension, similar schools.
    '''
    vectors = df.iloc[:, 2:].values #skip columns with id #s, school name
    clusters = range(2, 20)
    scores = np.zeros(len(clusters))
    for i, k in enumerate(clusters):
        km = KMeans(n_clusters=k)
        km.fit(vectors)
        scores[i] = silhouette_score(vectors, km.labels_)

    best_k = clusters[argmax(scores)]
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
    dist_matrix = squareform(pdist(vectors, metric='cosine'))
    link_matrix = linkage(dist_matrix, method='average')
    tree = cut_tree(link_matrix, n)
    return link_matrix, tree

'''
To think about: how to decide where best to cut the hierarchical tree?
'''

def plot_dendrogram(matr, fname=None):
    '''
    Given linkage matrix of schools, plot dendrogram
    '''
    plt.figure()
    dendrogram(matr)
    if fname != None:
        plt.savefig(fname)

def get_matches(df, n=20, ID=179867):
    clean = clean_school_data(df)
    link_matr, tree = make_hier_clusters(clean, n)

    idx = clean[clean['UNITID'] == ID].index[0]
    match_idx = np.where(tree == tree[idx][0])[0] # where returns a tuple
    match_df = clean.iloc[match_idx, :]
    return match_df

    # TODO make list of all id numbers for match schools, query to get complete info

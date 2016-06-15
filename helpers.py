import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram

def clean_school_data(df, cols):
    '''
    Impute missing values in schools data frame
    '''
    for col in cols:
        df.loc[df[col].isnull(), col ] = df[col].mean()
    return df

def plot_rates(df, cols):
    '''
    Given dataframe with rates across income levels, plot rates over years
    (in 'year' column)
    '''
    for col in cols:
        lab = " ".join(col.split('_')[:2])
        plt.plot(df['year'], data[col], '-o', label=lab)
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

def make_hier_clusters(df):
    '''
    Given dataframe of schools and attributes, use hierarchical clustering to
    find most similar schools.
    '''
    vectors = df.iloc[:, 2:].values
    dist_matrix = squareform(pdist(vectors, metric='cosine'))
    link_matrix = linkage(dist_matrix, method='average')
    return link_matrix

def plot_dendrogram(matr):
    '''
    Given linkage matrix of schools, plot dendrogram
    '''
    plt.figure()
    dendrogram(matr)

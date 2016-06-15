import pandas as pd
import matplotlib.pyplot as plt

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

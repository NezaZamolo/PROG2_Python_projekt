import matplotlib.pyplot as plt
import os

def plot_line(df, x_col, y_col, title, xlabel, ylabel, filename, legend_label=None):
    """
    Plot a line graph for the given DataFrame.
    :param df:
    :param x_col:
    :param y_col:
    :param title:
    :param xlabel:
    :param ylabel:
    :param filename:
    :param legend_label:
    :return:
    """
    plt.figure(figsize=(10, 5))
    plt.plot(df[x_col], df[y_col], label=legend_label or y_col)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if legend_label:
        plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    os.makedirs('plots', exist_ok=True)
    plt.savefig(filename)
    plt.close()

def plot_multi_line(df, group_col, x_col, y_col, title, xlabel, ylabel, filename):
    """
    Plot multiple lines for different groups in the DataFrame.
    :param df:
    :param group_col:
    :param x_col:
    :param y_col:
    :param title:
    :param xlabel:
    :param ylabel:
    :param filename:
    :return:
    """
    plt.figure(figsize=(12, 6))
    for group in df[group_col].unique():
        subset = df[df[group_col] == group]
        plt.plot(subset[x_col], subset[y_col], label=group)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    os.makedirs('plots', exist_ok=True)
    plt.savefig(f'plots/{filename}')
    plt.close()

def plot_histogram(series, dates, title, xlabel, ylabel, filename):
    """
    Plot a histogram for the given series and dates.
    :param series:
    :param dates:
    :param title:
    :param xlabel:
    :param ylabel:
    :param filename:
    :return:
    """
    plt.figure(figsize=(10, 5))
    plt.bar(dates, series, color='skyblue', edgecolor='black')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    os.makedirs('plots', exist_ok=True)
    plt.savefig(f'plots/{filename}')
    plt.close()
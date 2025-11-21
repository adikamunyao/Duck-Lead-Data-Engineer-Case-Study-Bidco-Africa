# pipeline_setup.py
import pandas as pd
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
import warnings

warnings.filterwarnings("ignore")
sns.set(style="whitegrid", font_scale=1.2)

# ----------------------------------------
# Load data function
# ----------------------------------------
def load_data(path):
    """
    Loads an Excel file and returns a DataFrame and a backup copy.
    """
    df = pd.read_excel(path)
    print(f"The data has {len(df):,} rows and {df.shape[1]} columns")
    return df, df.copy()

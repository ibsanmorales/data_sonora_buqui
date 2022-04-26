
#%%
import numpy as mp
import pandas as pd
import geopandas as gpd
import folium
from datetime import datetime

# %%
df = pd.read_csv("../data/raw/personas_desaparecidas/personas-desaparecidas-n.csv")

# %%

 a = df.agg('sum')
# %%

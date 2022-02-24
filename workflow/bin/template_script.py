import sys
import os
import glob
import pandas as pd
import argparse
import plotly.express as px

input_db_filename = sys.argv[1]
library_results_filename = sys.argv[2]
output_results_filename = sys.argv[3]

input_db_df = pd.read_csv(input_db_filename, sep=',')
original_results_df = pd.read_csv(library_results_filename, sep='\t')

print(original_results_df.columns)

# Choosing top scoring hit to be used as representative
original_results_df = original_results_df.sort_values(by=['MQScore'], ascending=False)
original_results_df["RT_Query"] = original_results_df["RT_Query"] / 60.0

results_df = original_results_df.groupby("#Scan#").first()

results_df = results_df[["Compound_Name", "RT_Query", "InChIKey", "InChIKey-Planar"]]
print(results_df.head())
print(input_db_df.head())
print(input_db_df.columns)

import seaborn as sns
import matplotlib.pyplot as plt


# Lets merge the data together
input_db_df["InChIKey-Planar"] = input_db_df["inchi_key"].apply(lambda x: x.split("-")[0])
merged_df = results_df.merge(input_db_df, how="inner", on="InChIKey-Planar")

#print(merged_df)
#ax = sns.regplot(data=merged_df, x="RT_Query", y="rt_peak", robust=True)
#plt.savefig('figure.png')

# Creating the regression
from sklearn.linear_model import LinearRegression, HuberRegressor

#reg = LinearRegression().fit(merged_df["RT_Query"].to_numpy().reshape(-1, 1), merged_df["rt_peak"].to_numpy().reshape(-1, 1))
#print(reg.coef_)
reg = HuberRegressor().fit(merged_df["RT_Query"].to_numpy().reshape(-1, 1), merged_df["rt_peak"].to_numpy().reshape(-1, 1))


# Let's apply it to the original results
original_results_df = original_results_df.merge(input_db_df, how="left", on="InChIKey-Planar")
original_results_df["modeled_rt_peak"] = reg.predict(original_results_df["RT_Query"].to_numpy().reshape(-1, 1))
original_results_df["delta_rt_to_model"] = original_results_df["modeled_rt_peak"] - original_results_df["rt_peak"]

original_results_df.to_csv(output_results_filename, sep="\t", index=False, na_rep="n/a")
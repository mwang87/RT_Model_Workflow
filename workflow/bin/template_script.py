import sys
import os
import glob
import pandas as pd
import argparse
import plotly.express as px

def main():
    parser = argparse.ArgumentParser(description='Script to run the workflow')
    parser.add_argument('input_db_filename', help='Input database tsv filename')
    parser.add_argument('library_results_filename', help='Library results filename')
    parser.add_argument('output_results_filename', help='Output results filename')
    parser.add_argument('--output_filtered_results_filename', help='Output filtered results filename', default=None)
    parser.add_argument('--output_results_scatter', help='output_results_scatter', default=None)
    parser.add_argument('--rt_tolerance', help='RT tolerance on the filtered output', default=0.1, type=float)
    parser.add_argument('--rt_min', help='RT minimum', default=0.0, type=float)
    parser.add_argument('--rt_max', help='RT maximum', default=50.0, type=float)
    parser.add_argument('--override', help='override', default="No")
    parser.add_argument('--override_slope', help='override_slope', default=1.0, type=float)
    parser.add_argument('--override_intercept', help='override_intercept', default=0.0, type=float)
    
    args = parser.parse_args()

    
    original_results_df = pd.read_csv(args.library_results_filename, sep='\t')

    print(original_results_df.columns)

    # Choosing top scoring hit to be used as representative
    original_results_df = original_results_df.sort_values(by=['MQScore'], ascending=False)
    original_results_df["RT_Query"] = original_results_df["RT_Query"] / 60.0

    # Filtering out RT min and max
    original_results_df = original_results_df[(original_results_df["RT_Query"] >= args.rt_min) & (original_results_df["RT_Query"] <= args.rt_max)]

    # Cleaning up the data frame
    results_df = original_results_df.groupby("#Scan#").first()

    results_df = results_df[["Compound_Name", "RT_Query", "InChIKey", "InChIKey-Planar"]]

    import seaborn as sns
    import matplotlib.pyplot as plt

    input_db_df = pd.read_csv(args.input_db_filename, sep='\t')
    input_db_df["InChIKey-Planar"] = input_db_df["inchi_key"].apply(lambda x: x.split("-")[0])

    # Let's apply it to the original results
    original_results_df = original_results_df.merge(input_db_df, how="left", on="InChIKey-Planar")
    

    # Creating a model
    if args.override == "Yes":
        original_results_df["modeled_rt_peak"] = args.override_slope * original_results_df["RT_Query"] + args.override_intercept
    else:
        # Creating the regression
        from sklearn.linear_model import LinearRegression, HuberRegressor

        merged_df = results_df.merge(input_db_df, how="inner", on="InChIKey-Planar")
        #reg = LinearRegression().fit(merged_df["RT_Query"].to_numpy().reshape(-1, 1), merged_df["rt_peak"].to_numpy().reshape(-1, 1))
        reg = HuberRegressor().fit(merged_df["RT_Query"].to_numpy().reshape(-1, 1), merged_df["rt_peak"].to_numpy().reshape(-1, 1))

        # Applying the model
        original_results_df["modeled_rt_peak"] = reg.predict(original_results_df["RT_Query"].to_numpy().reshape(-1, 1))

    # Calcuating Error
    original_results_df["delta_rt_to_model"] = original_results_df["modeled_rt_peak"] - original_results_df["rt_peak"]

    original_results_df.to_csv(args.output_results_filename, sep="\t", index=False, na_rep="n/a")

    # Now we can start filtering out hits
    if args.output_filtered_results_filename is not None:
        # here we can do the filtering based upon RT
        filtered_results_df = original_results_df[original_results_df["delta_rt_to_model"].abs() < args.rt_tolerance]

        # Finding the top hit
        filtered_results_df = filtered_results_df.sort_values(by=['MQScore'], ascending=False)
        filtered_results_df = filtered_results_df.groupby(['#Scan#', "SpectrumFile"]).first()

        # Outputting
        filtered_results_df.to_csv(args.output_filtered_results_filename, sep="\t", index=False, na_rep="n/a")


    if args.output_results_scatter is not None:
        with open(args.output_results_scatter, 'a') as f:
            # Plotting the results
            fig = px.scatter(original_results_df, x="RT_Query", y="rt_peak",
                            hover_name="Compound_Name", hover_data=["RT_Query", "modeled_rt_peak", "delta_rt_to_model"],
                            title="All Results, Observed RT vs DB True RT")
            f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))

            fig = px.scatter(filtered_results_df, x="RT_Query", y="rt_peak",
                            hover_name="Compound_Name", hover_data=["RT_Query", "modeled_rt_peak", "delta_rt_to_model"],
                            title="Filtered Results within {} min RT Error, Observed RT vs DB True RT".format(args.rt_tolerance))
            f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))

    

    
    

if __name__ == "__main__":
    main()
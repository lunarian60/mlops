#!/usr/bin/python 

""" 
    Skeleton code for k-means clustering mini-project.
"""
import pickle
import numpy
# import matplotlib.pyplot as plt
import sys
# sys.path.append("../tools/")
# from feature_format import featureFormat, targetFeatureSplit
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

import argparse
import os
import numpy as np


def featureFormat( dictionary, features, remove_NaN=True, remove_all_zeroes=True, remove_any_zeroes=False, sort_keys = False):
    """ convert dictionary to numpy array of features
        remove_NaN = True will convert "NaN" string to 0.0
        remove_all_zeroes = True will omit any data points for which
            all the features you seek are 0.0
        remove_any_zeroes = True will omit any data points for which
            any of the features you seek are 0.0
        sort_keys = True sorts keys by alphabetical order. Setting the value as
            a string opens the corresponding pickle file with a preset key
            order (this is used for Python 3 compatibility, and sort_keys
            should be left as False for the course mini-projects).
        NOTE: first feature is assumed to be 'poi' and is not checked for
            removal for zero or missing values.
    """


    return_list = []

    # Key order - first branch is for Python 3 compatibility on mini-projects,
    # second branch is for compatibility on final project.
    if isinstance(sort_keys, str):
        import pickle
        keys = pickle.load(open(sort_keys, "rb"))
    elif sort_keys:
        keys = sorted(dictionary.keys())
    else:
        keys = dictionary.keys()

    for key in keys:
        tmp_list = []
        for feature in features:
            try:
                dictionary[key][feature]
            except KeyError:
                print("error: key ", feature, " not present")
                return
            value = dictionary[key][feature]
            if value=="NaN" and remove_NaN:
                value = 0
            tmp_list.append( float(value) )

        # Logic for deciding whether or not to add the data point.
        append = True
        # exclude 'poi' class as criteria.
        if features[0] == 'poi':
            test_list = tmp_list[1:]
        else:
            test_list = tmp_list
        ### if all features are zero and you want to remove
        ### data points that are all zero, do that here
        if remove_all_zeroes:
            append = False
            for item in test_list:
                if item != 0 and item != "NaN":
                    append = True
                    break
        ### if any features for a given data point are zero
        ### and you want to remove data points with any zeroes,
        ### handle that here
        if remove_any_zeroes:
            if 0 in test_list or "NaN" in test_list:
                append = False
        ### Append the data point if flagged for addition.
        if append:
            return_list.append( np.array(tmp_list) )

    return np.array(return_list)


def targetFeatureSplit( data ):
    """
        given a numpy array like the one returned from
        featureFormat, separate out the first feature
        and put it into its own list (this should be the
        quantity you want to predict)

        return targets and features as separate lists

        (sklearn can generally handle both lists and numpy arrays as
        input formats when training/predicting)
    """

    target = []
    features = []
    for item in data:
        target.append( item[0] )
        features.append( item[1:] )

    return target, features


# def Draw(pred, features, poi, mark_poi=False, name="image.png", f1_name="feature 1", f2_name="feature 2"):
#     """ some plotting code designed to help you visualize your clusters """
#
#     ### plot each cluster with a different color--add more colors for
#     ### drawing more than five clusters
#     colors = ["b", "c", "k", "m", "g"]
#     for ii, pp in enumerate(pred):
#         plt.scatter(features[ii][0], features[ii][1], color = colors[pred[ii]])
#
#     ### if you like, place red stars over points that are POIs (just for funsies)
#     if mark_poi:
#         for ii, pp in enumerate(pred):
#             if poi[ii]:
#                 plt.scatter(features[ii][0], features[ii][1], color="r", marker="*")
#     plt.xlabel(f1_name)
#     plt.ylabel(f2_name)
#     plt.savefig(name)
#     plt.show()

    
def arg_setting():
    parser = argparse.ArgumentParser()

    # Hyperparameters are described here. In this simple example we are just including one hyperparameter.
    parser.add_argument("--n_clusters", type=int, default=-1)

    # Sagemaker specific arguments. Defaults are set in the environment variables.
    parser.add_argument("--output-data-dir", type=str, default=os.environ["SM_OUTPUT_DATA_DIR"])
    parser.add_argument("--model-dir", type=str, default=os.environ["SM_MODEL_DIR"])
    parser.add_argument("--train", type=str, default=os.environ["SM_CHANNEL_TRAIN"])

    args = parser.parse_args()
    return args


def main():
    args = arg_setting()
    
    ### load in the dict of dicts containing all the data on each person in the dataset
    data_dict = pickle.load( open(args.train + "/final_project_dataset_modified.pkl", "rb") )
    ### there's an outlier--remove it! 

    data_dict.pop("TOTAL", 0)


    ### the input features we want to use 
    ### can be any key in the person-level dictionary (salary, director_fees, etc.) 
    feature_1 = "salary"
    feature_2 = "from_messages"
    # feature_3 = 'total_payments'
    poi  = "poi"
    features_list = [poi, feature_1, feature_2]
    data = featureFormat(data_dict, features_list )
    poi, finance_features = targetFeatureSplit( data )

    # Scale the sample featureset 
    # scaler = MinMaxScaler() # Create instance of scaler class
    # scaler.fit(finance_features) # Access the fit method of scaler and create the values for scaling using the finance features 
    # finance_features = scaler.transform(finance_features) # Transform the finance features based on the scaling parameters generated by the scaler instanc
    # print scaler.transform([[200000.0, 1000000.0]])  # create the scaling for these datapoints (salary, bonus)

    ### in the "clustering with 3 features" part of the mini-project,
    ### you'll want to change this line to 
    ### for f1, f2, _ in finance_features:
    ### (as it's currently written, the line below assumes 2 features)
    # for f1, f2 in finance_features:
    #     plt.scatter( f1, f2 )
    #
    # plt.xlabel(feature_1)
    # plt.ylabel(feature_2)
    # plt.savefig(args.output_data_dir + "/clusters.png")
#     plt.show()

    ### cluster here; create predictions of the cluster labels
    ### for the data and store them to a list called pred
    kmeans = KMeans(n_clusters=args.n_clusters)
    kmeans.fit(finance_features)
    pred = kmeans.predict(finance_features)
    
    ## model save
    pickle.dump(kmeans, open(args.model_dir + "/kmeans.pkl", "wb"))

    ### rename the "name" parameter when you change the number of features
    ### so that the figure gets saved to a different file
    # try:
    #     Draw(pred, finance_features, poi, mark_poi=True, name=args.output_data_dir + "/clusters.pdf", f1_name=feature_1, f2_name=feature_2)
    # except NameError:
    #     print("no predictions object named pred found, no clusters to plot")

if __name__ == "__main__":
    main()


def model_fn(model_dir):
    """Deserialized and return fitted model

    Note that this should have the same name as the serialized model in the main method
    """
    with open(model_dir + "/kmeans.pkl", "rb") as f:
        model = pickle.load(f)
    return model

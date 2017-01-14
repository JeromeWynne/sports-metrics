""" sports-metrics // bears """
# Created 10-12-2016
# Last updated 10-12-2016
# Utility functions for Pandas
#       Function name            |       Dependencies        |       Description
# NormalisedVarianceThreshold    | pd                        | Returns a pd.VarianceThreshold configured to extract a given proportion of the data's variance.


import pandas as pd
import numpy as np
from sklearn.feature_selection import VarianceThreshold

def NormalisedVarianceThreshold(data, cum_var=0.95):
    # Returns a sklearn.VarianceThreshold object with a threshold that will
    # retain [cum_var]% of data's variance when used for transformation.
    # data -> pd.DataFrame // Data to fit the VarianceThreshold object to.
    # cum_var -> float // Percentage of data's variance to retain.
    total_variance = VarianceThreshold().fit(data).variances_.sum()
    vt = VarianceThreshold(threshold=(1 - cum_var)*total_variance)
    return vt

import os
import random
import pandas as pd 
import numpy as np
from pseudo import graph_viz
import uuid

NUM_USER = 100
NUM_FEAT = 30


def generate_pseudo_data():
    csn_ids = [uuid.uuid4() for i in range(NUM_USER)]
    feature_names = ["feature_%s" % i for i in range(NUM_USER)]
    user_property = {}
    for csn in csn_ids:
        user_property[csn] = {feat: random.random() for feat in feature_names}
    user_linkage = []
    for i in range(NUM_USER):
        for j in range(i, NUM_USER):
            if random.randint(0,2) % 2 == 0:
                user_linkage.append([csn_ids[i],csn_ids[j]])
    return user_property, user_linkage


if __name__ == '__main__':
    user_property, user_linkage = generate_pseudo_data()

    # Plot
    G = graph_viz.GraphViz()
    G.plot_risk_graph_3d(user_property, user_linkage)

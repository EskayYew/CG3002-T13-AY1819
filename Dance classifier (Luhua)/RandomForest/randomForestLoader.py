from sklearn.externals import joblib
import numpy as np


def random_forest_loader(data):
    rdf_module = joblib.load("randomforest")
    data_1 = data[0:50]
    data_2 = data[50:100]
    data_3 = data[100:150]
    result_1 = rdf_module.predict(data_1)
    result_2 = rdf_module.predict(data_2)
    result_3 = rdf_module.predict(data_3)

    if result_1 == result_2:
        return result_1

    elif result_1 == result_3:
        return result_2

    elif result_2 == result_3:
        return result_3

    else:
        return 'Cannot determine'

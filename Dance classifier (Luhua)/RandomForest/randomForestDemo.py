import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import itertools
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

pd.options.display.max_rows = 20

train_data = pd.read_csv('train.csv')

# print(train_data.describe().transpose())

# STANDING 1
# SITTING 2
# LAYING 3
# WALKING 4
# WALKING DOWNSTAIRS 5
# WALKING UPSTAIRS 6

X, y = train_data.drop('Activity', axis=1), train_data['Activity']
X = X[1:][0:]
y = y[1:]

class_names = y.unique()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

rdf = RandomForestClassifier()
rdf.fit(X_train, y_train)

print(f"Accuracy of train data: {rdf.score(X_train, y_train)}")
print(f"Accuracy of test data: {rdf.score(X_test, y_test)}")

y_pred = rdf.predict(X_test)


cnf_matrix = confusion_matrix(y_test, y_pred)
np.set_printoptions(precision=2)

rdf.figure()


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


plot_confusion_matrix(cnf_matrix, classes=class_names, normalize=True,
                      title='Normalized confusion matrix')

plt.show()




















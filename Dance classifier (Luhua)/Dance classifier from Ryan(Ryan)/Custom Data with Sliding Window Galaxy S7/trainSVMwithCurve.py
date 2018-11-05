import ReadCSVToList
import numpy as np

WALKING_FILE = "Walking/WalkingSegmented.csv"

SQUATTING_FILE = "Squatting/SquattingSegmented.csv"

WAVING_FILE = "Waving/WavingSegmented.csv"

DATA_FILES = [WALKING_FILE, WAVING_FILE, SQUATTING_FILE]

TRAINING_LABELS = []
FINAL_TRAINING_DATA = []

TEST_DATA = []
TEST_DATA_LABELS = []

def loadData():
    for files in DATA_FILES:
        counter = 0
        temp_data = ReadCSVToList.convertFileToList(files)
        label = files[:6] #Cut short filename
        
        for row in temp_data:
            FINAL_TRAINING_DATA.append(row)
            TRAINING_LABELS.append(label)

loadData()

#print(TRAINING_LABELS)
#print(TEST_DATA_LABELS)

X = np.array(FINAL_TRAINING_DATA)
y = np.array(TRAINING_LABELS)

from sklearn.svm import SVC
clf = SVC(decision_function_shape='ovo')
clf.fit(X, y)

from sklearn.model_selection import cross_val_score
scores = cross_val_score(clf, X, y, cv=2)
print("Accuracy: %0.5f (+/- %0.5f)" % (scores.mean(), scores.std() * 2))

from sklearn.model_selection import validation_curve
import matplotlib.pyplot as plt

param_range = np.logspace(-6, -1, 5)
train_scores, test_scores = validation_curve(
    clf, X, y, param_name="gamma", param_range=param_range,
    cv=10, scoring="accuracy", n_jobs=1)
train_scores_mean = np.mean(train_scores, axis=1)
train_scores_std = np.std(train_scores, axis=1)
test_scores_mean = np.mean(test_scores, axis=1)
test_scores_std = np.std(test_scores, axis=1)

plt.title("Validation Curve with SVM")
plt.xlabel("$\gamma$")
plt.ylabel("Score")
plt.ylim(0.0, 1.1)
lw = 2
plt.semilogx(param_range, train_scores_mean, label="Training score",
             color="darkorange", lw=lw)
plt.fill_between(param_range, train_scores_mean - train_scores_std,
                 train_scores_mean + train_scores_std, alpha=0.2,
                 color="darkorange", lw=lw)
plt.semilogx(param_range, test_scores_mean, label="Cross-validation score",
             color="navy", lw=lw)
plt.fill_between(param_range, test_scores_mean - test_scores_std,
                 test_scores_mean + test_scores_std, alpha=0.2,
                 color="navy", lw=lw)
plt.legend(loc="best")
plt.show()

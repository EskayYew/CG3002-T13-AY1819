FOR FINAL SUBMISSION: CSV FILES CONTAINING DATA HAVE BEEN OMITTED TO SAVE SPACE

Training the model

1. Ensure that the following files/folders are in the same folder:
	a. trainNeuralNetCorrelation.py
	b. ExtractFeatures.py
	c. ReadCSVToList.py
	d. SegmentData.py
	e. "Training" folder with all the CSV files in their corresponding sub-folders.

2. Open the trainNeuralNetCorrelation.py file. Ensure that the folder paths and labels are correct.
2a. You may change the labels and folder paths accordingly.

Ensure that the label names are identical as listed in the README file in the Deployment folder.

3. To save the "Scaler" and "Model", change the SAVE_FLAG from False to True.

Evaluating the Model using CV testing

1. Ensure that the following files/folders are in the same folder:
	a. EvaluateNeuralNetCorrelation.py
	b. ExtractFeatures.py
	c. ReadCSVToList.py
	d. SegmentData.py
	e. "Training" folder with all the CSV files in their corresponding sub-folders.

2. Open the EvaluateNeuralNetCorrelation.py file. Ensure that the folder paths and labels are correct.
2a. You may change the labels and folder paths accordingly.

3. The model used for CV testing has the variable name "NN_CV". As per warning, do not fit any data to this model.

4. To switch between random CV testing and K-fold CV, change the "cv" variable in the following line:

scores = cross_val_score(SVM_CV, X, y, cv=rs)

Where rs = random shuffle cv, Any positive integer, N = K-Fold CV, where K will be determined by N.

4a. You can control how much data to restrict by changing the "test_size" variable in the following line:

rs = ShuffleSplit(n_splits=30, random_state=None, test_size=0.25)

Where "test_size" takes in a float between 0.0 and 1.0.

5. **VERY IMPORTANT** THE NN_CV MODEL WILL NOT BE SAVED. IT IS MERELY A TOOL TO ESTIMATE PERFORMANCE OF OUR TRAINED MODEL.
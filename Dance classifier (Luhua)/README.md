This is the Random forest model I have explored(Luhua).

--------How to Generate the model: 

put the csv of different moves into respective folder in "ClassifiedTrainingSet"

execute the file "randomForest_multiprediction" or "randomForest_withSegmentation"

a model will be generated and the accuracy validation would be shown in the console.

you can check if the model satisfies your requirement

for Gaussian Naive Bays, the process is the same

Note that data processing/segmentation and feature extraction is included inside the file, in order to minimize the time for function calls. The separate "DataProcessing" folder is only for illustration purpose 



---------How to deploy the model in RPi

copy the model you generated altogether with the "randomForestLoader"

The loader will take in 2 seconds/100 points of data and call the model then do the prediction



---------Difference between "randomForest_multiprediction" and "randomForest_withSegmentation"

1. Random Forest with multiPrediction 

The first one will take in 2 seconds of data and do 3 predictions. 
each prediction will take data of 1 second and with sliding window of 0.5 seconds, this will result in 3 consecutive predictions
we need to score at least 2 out of 3 in order for the system to confidently determine the result.


2. Random Forest with Segmentation

This is the original version of random forest
The second model will just take in 2 seconds of data and do one prediction, window size is 2 seconds with a sliding window of 1 second

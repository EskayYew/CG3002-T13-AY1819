IMPORTANT THINGS TO TAKE NOTE

1. Sensors are to be read at 50Hz. 
2. Window Size is 3 seconds long - i.e. 150 datapoints.
3. POWER SENSOR DATA SHOULD NOT BE INCLUDED IN THE WINDOW FED TO THE MODEL.

HOW TO USE

1. Ensure that the following files are located in the same folder:
	a. The Model.py file
	b. The saved model itself (Either NeuralNet or SVM. IT HAS NO FILE EXTENSION)
	c. The saved scaler for the model. (Either NeuralNet_Scaler or SVM_Scaler. IT HAS NO FILE EXTENSION)
	d. The ExtractFeatures.py file

2. Import the Model.py file and instantiate the model object.
	e.g. model = DanceClassifierNN()

3. To get a prediction, call the detectMove(window) function. It takes in a 1-D list of data.
	a. If the window size is incorrect, it will print an error message and return None.
	b. Otherwise, it will return a prediction.

4. Prediction is given in the form of a numpy array with 1 item. Access it by indexing first element.
	e.g. prediction[0] - will give the prediction in the form of a String.

4a. If prediction is unsure, the prediction will be ["UNSURE"]

Below are the names of the predictions

CHICKEN
COWBOY
IDLE_A
MERMAID
NUMBER6
NUMBER7
SALUTE
SIDESTEP
SWING
TURNCLAP
WIPERS
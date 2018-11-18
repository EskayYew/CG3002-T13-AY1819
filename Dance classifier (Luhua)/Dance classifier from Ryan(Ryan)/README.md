# Dance Classifier

Features to explore

1. Kurtosis
2. Average peak frequency
3. Correlation between time-series data
4. Stuff in Frequency Domain
5. Energy: Energy is calculated as the sum of the squared discrete FFT component magnitudes of the signal from each sensor axis. The sum is then divided by the window length for normalization.


To COMMS People
Eventually when we get the whole system together, we will work together to create a "prediction object".
1. When we init the object, it will load one of our ML algorithms.
2. From then on, it should be as simple as calling a "simple" function with the input data for a prediction. 
2a. Naturally, the inner workings of the "simple" function will be abstracted out into several smaller helper functions which will extract the features and add it to the input data before feeding it into the ML algorithm. This is open for discussion as to whether you want to process the data before or after calling the ML function.

Ideal sampling rate should be at least 45 Hz. Source: Optimising sampling rates for accelerometer-based human activity recognition
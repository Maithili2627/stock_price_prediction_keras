# -*- coding: utf-8 -*-
"""stock-price-prediction-keras.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/rawar/tensorflow-notebooks/blob/master/stock_price_prediction_keras.ipynb

# Predict stock prices  with Long short-term memory (LSTM)

This simple example will show you how LSTM models predict time series data. Stock market data is a great choice for this because it's quite regular and widely available via the Internet.

## Install requirements
We install Tensorflow 2.0 with GPU support first
"""

!pip install tensorflow-gpu==2.0.0-alpha0

!pip install pandas-datareader

!apt install graphviz

!pip install pydot pydot-ng

"""## Introduction

LSTMs are very powerful in sequence prediction problems. They can store past information.

## Loading the dataset
I use pandas-datareader to get the historical stock prices from Yahoo! finance. For this example, I get only the historical data till the end of *training_end_data*.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas_datareader import data

tickers = 'AAPL'

start_date = '1980-12-01'
end_date = '2018-12-31'

stock_data = data.get_data_yahoo(tickers, start_date, end_date)

stock_data.head(10)

stock_data.describe()

stock_data_len = stock_data['Close'].count()
print(stock_data_len)

"""I'm only interested in *close* prices"""

close_prices = stock_data.iloc[:, 1:2].values
print(close_prices)

"""Of course, some of the weekdays might be public holidays in which case no price will be available. For this reason, we will fill the missing prices with the latest available prices"""

all_bussinessdays = pd.date_range(start=start_date, end=end_date, freq='B')
print(all_bussinessdays)

close_prices = stock_data.reindex(all_bussinessdays)
close_prices = stock_data.fillna(method='ffill')

close_prices.head(10)

"""The dataset is now complete and free of missing values. Let's have a look to the data frame summary:

## Feature scaling
"""

training_set = close_prices.iloc[:, 1:2].values

print(training_set)

from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range = (0, 1))
training_set_scaled = sc.fit_transform(training_set)
print(training_set_scaled.shape)

"""LSTMs expect the data in a specific format, usually a 3D tensor. I start by creating data with 60 days and converting it into an array using NumPy. Next, I convert the data into a 3D dimension array with feature_set samples, 60 days and one feature at each step."""

features = []
labels = []
for i in range(60, stock_data_len):
    features.append(training_set_scaled[i-60:i, 0])
    labels.append(training_set_scaled[i, 0])

features = np.array(features)
labels = np.array(labels)

features = np.reshape(features, (features.shape[0], features.shape[1], 1))

print(labels)

print(features)

"""Feature tensor with three dimension: features[0] contains the ..., features[1] contains the last 60 days of values and features [2] contains the  ..."""

print(features.shape)

"""## Create the LSTM network
Let's create a sequenced LSTM network with 50 units. Also the net includes some dropout layers with 0.2 which means that 20% of the neurons will be dropped.
"""

import tensorflow as tf

model = tf.keras.models.Sequential([
    tf.keras.layers.LSTM(units = 50, return_sequences = True, input_shape = (features.shape[1], 1)),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.LSTM(units = 50, return_sequences = True),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.LSTM(units = 50, return_sequences = True),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.LSTM(units = 50),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(units = 1)
])

print(model.summary())

#tf.keras.utils.plot_model(model, to_file='my_model.png')

# Run tensorboard with the logdir
#import os
#LOG_BASE_DIR = './log'
#os.makedirs(LOG_BASE_DIR, exist_ok=True)

#!ls -l log

"""## Load the Colab TensorBoard extention and start TensorBoard inline"""

#%load_ext tensorboard.notebook
#%tensorboard --logdir {LOG_BASE_DIR}

"""## Define a TensorBoard callback"""

#import datetime
#logdir = os.path.join(LOG_BASE_DIR, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))

#from tensorflow.keras.callbacks import TensorBoard

#tbCallBack = TensorBoard(logdir,histogram_freq=1)

"""The model will be compiled and optimize by the adam optimizer and set the loss function as mean_squarred_error"""

model.compile(optimizer = 'adam', loss = 'mean_squared_error')

#import os
#print(os.environ)

#tf.test.gpu_device_name()

#from tensorflow.python.client import device_lib
#device_lib.list_local_devices()

from time import time
start = time()
history = model.fit(features, labels, epochs = 20, batch_size = 32, verbose = 1)
end = time()

print('Total training time {} seconds'.format(end - start))

#  [samples, days, features]
print(features.shape)

testing_start_date = '2019-01-01'
testing_end_date = '2019-04-10'

test_stock_data = data.get_data_yahoo(tickers, testing_start_date, testing_end_date)

test_stock_data.tail()

test_stock_data_processed = test_stock_data.iloc[:, 1:2].values

print(test_stock_data_processed.shape)

all_stock_data = pd.concat((stock_data['Close'], test_stock_data['Close']), axis = 0)

inputs = all_stock_data[len(all_stock_data) - len(test_stock_data) - 60:].values
inputs = inputs.reshape(-1,1)
inputs = sc.transform(inputs)

X_test = []
for i in range(60, 129):
    X_test.append(inputs[i-60:i, 0])

X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
predicted_stock_price = model.predict(X_test)
predicted_stock_price = sc.inverse_transform(predicted_stock_price)

plt.figure(figsize=(10,6))  
plt.plot(test_stock_data_processed, color='blue', label='Actual Apple Stock Price')  
plt.plot(predicted_stock_price , color='red', label='Predicted Apple Stock Price')  
plt.title('Apple Stock Price Prediction')  
plt.xlabel('Date')  
plt.ylabel('Apple Stock Price')  
plt.legend()  
plt.show()

#inputs = inputs.reshape(-1,1)
#inputs = sc.transform(inputs)


test_inputs = test_stock_data_processed.reshape(-1,1)
test_inputs = sc.transform(test_inputs)


print(test_inputs.shape)

test_features = []
for i in range(60, 291):
    test_features.append(test_inputs[i-60:i, 0])
    
test_features = np.array(test_features)

test_features = np.reshape(test_features, (test_features.shape[0], test_features.shape[1], 1))  
print(test_features.shape)

predicted_stock_price = model.predict(test_features)

predicted_stock_price = sc.inverse_transform(predicted_stock_price)
print(predicted_stock_price.shape)

print(test_stock_data_processed.shape)

plt.figure(figsize=(10,6))  
plt.plot(test_stock_data_processed, color='blue', label='Actual Apple Stock Price')  
plt.plot(predicted_stock_price , color='red', label='Predicted Apple Stock Price')  
plt.title('Apple Stock Price Prediction')  
plt.xlabel('Date')  
plt.ylabel('Apple Stock Price')  
plt.legend()  
plt.show()

"""## Download the model and the weights"""

from google.colab import files

model_json = model.to_json()
with open("model.json", "w") as json_file:
  json_file.write(model_json)

files.download("model.json")

model.save('weights.h5')
files.download('weights.h5')
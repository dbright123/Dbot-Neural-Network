from tensorflow.keras.layers import Input,Dense,LSTM,Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import SGD,Adam
from tensorflow.keras.callbacks import TensorBoard
import MetaTrader5 as mt5
import numpy as np
import joblib
import time
from datetime import datetime,timezone

print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)




from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
import MetaTrader5 as mt5
import numpy as np
import joblib
import time
from datetime import datetime,timezone
import joblib

print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)

def r_squared(y_true, y_pred):
  mean_y_true = np.mean(y_true)
  ss_tot = np.sum((y_true - mean_y_true)**2)
  ss_res = np.sum((y_true - y_pred)**2)
  r_squared = 1 - ss_res / ss_tot
  
  return r_squared

lot = 0.01

market = "GBPUSD"

models = [load_model(market+"m15.keras"),load_model(market+"1h.keras"),load_model(market+"4h.keras")]
sc_xs = [joblib.load(market+" sc_xm15.joblib"),joblib.load(market+" sc_x1h.joblib"),joblib.load(market+" sc_x4h.joblib")]
sc_ys = [joblib.load(market+" sc_ym15.joblib"),joblib.load(market+" sc_y1h.joblib"),joblib.load(market+" sc_y4h.joblib")]
tf = [mt5.TIMEFRAME_M15,mt5.TIMEFRAME_H1,mt5.TIMEFRAME_H4]

if not mt5.initialize():
  print('Initialization failed, check internet connection. You must have Meta Trader 5 installed.')

else: 
  print(mt5.account_info()._asdict())
  print("\n")
  print(mt5.terminal_info()._asdict())
  while(True):
    terminal = mt5.terminal_info()
    if(terminal.connected == True and terminal.trade_allowed == True):
      account = mt5.account_info()
      print(account)
      print(account.equity)
      print("AI is functional loading "+market)

      
      for n in range(len(tf)):
        print("checking prediction standards on major timeframes m15 , 1h, and 4h")
        rates = mt5.copy_rates_from_pos(market, tf[n], 0, 500)
        model = models[n]
        sc_x = sc_xs[n]
        sc_y = sc_ys[n]
        #print(rates)
        print(rates.shape)
        data = []
        close_price = []
        

        for i in range(len(rates)):
          data.append([rates[i][1],rates[i][5]])
          close_price.append(rates[i][4])


        data = np.array(data)
        close_price = np.array(close_price)
        data = sc_x.transform(data)

        data = data.reshape((data.shape[0], 1, data.shape[1])) # 3 dimensaional data

        y_pred = model.predict(data)

        y_pred = sc_y.inverse_transform(y_pred.reshape((len(y_pred),1)))
        y_pred = y_pred.reshape(-1)

        score =  r_squared(close_price[-100:],y_pred[-100:])
        print("stage 1")
        print(score, " is the current prediction model performance", n)

        if(score < 0.50):
          print("Please the system will need a lot of retraining on the neural network due to poor prediction on past data")
          print("Showing reason for statement")
          
          quit()
      
      #checking time for best trading which is on 9am to 1pm which is on london , new york overlap

      now_utc = datetime.utcnow()

      # Convert the UTC datetime to GMT +0
      now_gmt0 = now_utc.astimezone(timezone.utc)

      # Get the year, month, day, and hour from the GMT +0 datetime
      hour = now_gmt0.hour + 1
      mins = now_gmt0.minute
      # Print the results
      print("Hour:", hour,": Minute:", mins)

      if(hour > 8 and hour < 16):
        data1h = 0
        data4h = 0
        rates = mt5.copy_rates_from_pos(market, tf[1], 0, 1)
        data1h = rates[0][0]
        print(data1h)
        rates = mt5.copy_rates_from_pos(market, tf[2], 0, 1)
        data4h = rates[0][0]
        print(data4h)

        if(data1h == data4h):## Entering new market 
          pass
        else:
          print("Please wait !!!! as robot cant enter market now because it will be late")



      else:
        print("This system is program to trade on london session only, please wait for the session")
        time.sleep(20)
      ## Maintaining existing market

    else:
      print("Please make sure metatrade 5 has internet and algo Trade is Turn On")
      time.sleep(20)

quit()
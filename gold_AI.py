from tensorflow.keras.models import load_model

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

market = "XAUUSD"
model = load_model(market+".keras")

sc_x = joblib.load(market+" sc_x.joblib")
sc_y = joblib.load(market+" sc_y.joblib")

tf = mt5.TIMEFRAME_M15
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
            
            rates = mt5.copy_rates_from_pos(market, tf, 0, 500)
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
            print(score, " is the current prediction model performance")

            if(score <= 0.60):
                print(market+" will need re-training, please train the model again or check program for error, the prediction is too poor")
                print("checking other market")

                time.sleep(10)
            else:
                rates = mt5.copy_rates_from_pos(market, tf, 0, 1)
                print(rates)
                data=[[rates[0][1],rates[0][5]]]
                close_price = [rates[0][4]]
                data = np.array(data)
                print(data)
                close_price = np.array(close_price)
                print(close_price)
                data = sc_x.transform(data)

                data = data.reshape((data.shape[0], 1, data.shape[1])) # 3 dimensaional data

                y_pred = model.predict(data)
    
                y_pred = sc_y.inverse_transform(y_pred.reshape((len(y_pred),1)))
                y_pred = y_pred.reshape(-1)


                now_utc = datetime.utcnow()

                # Convert the UTC datetime to GMT +0
                now_gmt0 = now_utc.astimezone(timezone.utc)

                # Get the year, month, day, and hour from the GMT +0 datetime
                hour = now_gmt0.hour + 1
                mins = now_gmt0.minute
                # Print the results
                print("Hour:", hour,": Minute:", mins)

                allow_trade = True
                if(mins > 30): allow_trade = False
                else: allow_trade = True    
                #Starting trade operation
        
                symbol = market
                price = mt5.symbol_info_tick(symbol).bid
                print("current price for ",market," is ",price, " predicted price is ",y_pred[0], " difference in price is ",abs(price - y_pred[0]))

                
                permit_trade = False
                modify_trade = False
                o_price = 0
                c_price = 0
                profit = 0
                lot_size = 0
                order_type = 0
                sl = 0.0
                target_order = None

                
                if(y_pred[0] > price):
                    price = mt5.symbol_info_tick(symbol).ask
                    #buying a market
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": lot,
                        "type": mt5.ORDER_TYPE_BUY,
                        "price": price,
                        "sl": 0.0,
                        "tp": 0.0,
                        "deviation": 8,
                        "magic": 0,
                        "comment": "Dbot_ML",
                        "type_time": mt5.ORDER_TIME_GTC,
                       
                    }
                    permit_trade = True
                elif(y_pred[0] < price):
                    price = mt5.symbol_info_tick(symbol).bid
                    #Selling a market
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": lot,
                        "type": mt5.ORDER_TYPE_SELL,
                        "price": price,
                        "sl": 0.0,
                        "tp": 0.0,
                        "deviation": 8,
                        "magic": 0,
                        "comment": "Dbot_ML",
                        "type_time": mt5.ORDER_TIME_GTC,
                        
                    }
                    permit_trade = True



                print("Stage 2")
                if(permit_trade):
                    price = mt5.symbol_info_tick(symbol).bid
                    permit_trade = True
                    
                if(permit_trade):
                    print("Trade activation on "+market)

                    if(mt5.positions_total() == 0):
                        #Ordering the trade
                        #here
                        if(allow_trade):
                            result=mt5.order_send(request)
                            print(result)

                    else:
                        #checking if the trade exist so as to modified it 
                        order_symbols = mt5.positions_get()

                        for order_symbol in order_symbols:
                            #print(order_symbol)
                            if(market == order_symbol.symbol):
                                print("seen")
                                target_order = order_symbol
                                print(target_order)
                                print("Stage 3")
                                o_price = target_order.price_open
                                c_price = target_order.price_current
                                profit = target_order.profit
                                lot_size = target_order.volume
                                order_type = target_order.type

                                print("open price ", o_price)
                                print("close_price ",c_price)
                                print("profit ",profit)
                                print("lot size ",lot_size)
                                print("order type ",order_type)
                                if(order_type == 0 and target_order.tp < o_price):
                                    result = mt5.Close(target_order.symbol,ticket=target_order.ticket)
                                    print(result)
                                elif(order_type == 1 and target_order.tp > o_price):
                                    result = mt5.Close(target_order.symbol,ticket=target_order.ticket)
                                    print(result)
                                modify_trade = True
                                break


                    if(modify_trade == False):
                       # here
                        if(allow_trade):
                            result=mt5.order_send(request)
                            print(result)


                print("Stage 4")
                close_trade = False
                #current stage
                if(modify_trade):
                    price = mt5.symbol_info_tick(symbol).bid
                    close_trade = False

                    if(target_order.type == 0):
                        if(y_pred[0] < price and mins > 30):
                            result = mt5.Close(target_order.symbol,ticket=target_order.ticket)
                            print(result)

                    elif(target_order.type == 1):
                        if(y_pred[0] > price and mins > 30):
                            result = mt5.Close(target_order.symbol,ticket=target_order.ticket)
                            print(result)

                    if(target_order.profit > 0.50):
                        result = mt5.Close(target_order.symbol,ticket=target_order.ticket)
                        print(result)

                print("Stage 5")
                print(mt5.last_error())
                time.sleep(5)
            
        else:
            print("Please make sure metatrade 5 has internet and algo Trade is Turn On")
            time.sleep(5)
    
mt5.shutdown()
quit()


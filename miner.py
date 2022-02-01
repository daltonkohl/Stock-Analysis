import yfinance
import csv
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import signal

global interrupted
interrupted = False

def signal_handler(signal, frame):
    global interrupted
    if interrupted == True:
        exit(0)
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)
symbols_file = open("constituents_csv.csv", "r")
symbols = symbols_file.readline().split(",")
symbols = symbols[:200]



f = open("stock_data_normalized.txt", "w")
writer = csv.writer(f)

#tickers = ["CNNA", "CKSG", "WRAP", "BBIG", "VPOR", "SVAP", "SPXC", "SOLI", "NWL", "HON", "MLCG", "EFTI", "BORK", "AGTX", "ARCW", "CVR", "CIX", "BOOM", "WIRE", "FRD", "ROCK", "VATE", "MLI", "MATW", "NNBR", "PERT", "SVT", "ROLL", "TLDN", "TKR", "VMI", "AOS", "AVOZ", "APOG", "ARCS", "CPWY", "CNR", "GFF", "TILE", "LGBS", "LGNC", "LYTS", "MAS", "DOOR", "MEGH", "NDDG", "PGTI", "PLPC"]
#print(len(tickers))
#broken = ["3M", "BMMX", ]

for ticker in symbols:
    try:
        stock = yfinance.Ticker(ticker)
        bs_dict = stock.get_balancesheet(as_dict=True)
        cf_dict = stock.get_cashflow(as_dict=True)
        fin_dict = stock.get_financials(as_dict=True)

        #print(yfinance.download('VXZ'))


        #data = yfinance.download(ticker,start='2019-03-31',end='2019-04-30')
        #close_data = data['Close'].head(1).to_string()
        #close_data = close_data.split()
        #REMOVED: TOTAL REVENUE, TOTAL ASSETS
        #CHANGED: TOTAL LIABILITIES -> NET ASSETS

        balance_sheet_list = ['Total Liab', 'Cash','Total Current Liabilities','Total Current Assets','Net Tangible Assets']
        cash_flow_list = ['Change In Cash','Total Cash From Operating Activities','Dividends Paid']
        fin_list = ['Research Development','Gross Profit']
        price_list = ['Current Price','Increase In Price From 1yr','Increase In Price From 2yr','Increase In Price From 3yr','Increase In Price From 4yr','Increase In Price From 5yr']
        dowj_list = ['DOWJ at current', 'DOWJ increase 1yr', 'DOWJ increase 2yr','DOWJ increase 3yr','DOWJ increase 4yr','DOWJ increase 5yr', "y-value"]
        dates = []
        date_format = '%Y-%m-%d'


        valid_line = True

        key_list = []
        for key in bs_dict.keys():
            key_list.append(key)
            date = key.date()
            dates.append(date)




        key_list.pop(0)
        dates_original = dates.copy()
        dates.pop(0)

        y_index = 0
        count = 0
        for key in key_list:

            date = dates_original[y_index]
            next_day = date + timedelta(days=1)
            new_date1 = date.strftime(date_format)
            new_date2 = next_day.strftime(date_format)
            data = yfinance.download(ticker,start=new_date1,end=new_date2)

            while data.empty:
                next_day += timedelta(days=1)
                new_date2 = next_day.strftime(date_format)
                data = yfinance.download(ticker,start=new_date1,end=new_date2)

            close_data = data['Close'].head(1).to_string()
            close_data = close_data.split()
            y = close_data[2]
            print("Y value is: " + str(y))

            y_index += 1


            attributes_dict_1 = bs_dict[key]
            value_list_1 = []
            for key2 in attributes_dict_1.keys():
                if key2 in balance_sheet_list:
                    if attributes_dict_1[key2] != None:
                        if key2 == "Total Liab":
                            value_list_1.append(((float(attributes_dict_1["Total Assets"]) -  float(attributes_dict_1[key2])))/float(attributes_dict_1["Total Assets"]))
                            print(attributes_dict_1[key2])
                        elif key2 == "Cash" or key2 == "Total Current Assets" or key2 == "Net Tangible Assets":
                            value_list_1.append(float(attributes_dict_1[key2])/float(attributes_dict_1["Total Assets"]))
                        elif key2 == "Total Current Liabilities":
                            value_list_1.append(float(attributes_dict_1[key2])/float(attributes_dict_1["Total Liab"]))



            attributes_dict_2 = cf_dict[key]
            attributes_dict_3 = fin_dict[key]
            value_list_2 = []
            for key3 in attributes_dict_2.keys():
                if key3 in cash_flow_list:
                    if attributes_dict_2[key3] != None:
                        if key3 == "Change In Cash" or key3 == "Total Cash From Operating Activities" or key3 == "Dividends Paid":
                            value_list_2.append(float(attributes_dict_2[key3])/float(attributes_dict_3["Gross Profit"]))


            value_list_3 = []
            for key4 in attributes_dict_3.keys():
                if key4 in fin_list:
                    if attributes_dict_3[key4] != None:
                        try:
                            if key4 == "Gross Profit":
                                value_list_3.append(float(attributes_dict_3[key4])/float(attributes_dict_3["Total Revenue"]))
                            elif key4 == "Research Development":
                                value_list_3.append(float(attributes_dict_3[key4])/float(attributes_dict_3["Total Revenue"]))
                        except:
                            print("nice try dirty data")

            value_list_4 = []
            value_list_5 = []
            date = dates[count]
            next_day = date + timedelta(days=10)
            prev_day = date - timedelta(days=10)
            new_date1 = date.strftime(date_format)
            new_date2 = next_day.strftime(date_format)
            data = yfinance.download(ticker,start=new_date1,end=new_date2)
            dowj_data = yfinance.download('SPY',start=new_date1,end=new_date2)

            counter = 0
            while data.empty:
                if interrupted:
                    valid_line = False
                    interrupted = False
                    break
                if counter > 10:
                    valid_line = False
                    break
                next_day += timedelta(days=10)
                prev_day -= timedelta(days=10)
                new_date2 = next_day.strftime(date_format)
                data = yfinance.download(ticker,start=new_date1,end=new_date2)
                if data.empty:
                    new_date2 = prev_day.strftime(date_format)
                    data = yfinance.download(ticker,start=new_date2,end=new_date1)
                counter += 1


            counter = 0
            while dowj_data.empty:
                if interrupted:
                    valid_line = False
                    interrupted = False
                    break
                if counter > 10:
                    valid_line = False
                    break
                next_day += timedelta(days=10)
                prev_day -= timedelta(days=10)
                new_date2 = next_day.strftime(date_format)
                dowj_data = yfinance.download("SPY",start=new_date1,end=new_date2)
                if data.empty:
                    new_date2 = prev_day.strftime(date_format)
                    dowj_data = yfinance.download("SPY",start=new_date2,end=new_date1)
                counter += 1

            if valid_line:
                close_data = data['Close'].head(1).to_string()
                close_data = close_data.split()
                dowj_close_data = dowj_data['Close'].head(1).to_string()
                dowj_close_data = dowj_close_data.split()

            current_price = float(close_data[2])
            print("Current price is: " + str(current_price))
            current_dowj_price = float(dowj_close_data[2])

            for i in range(5):
                print("*")
                date = date - timedelta(days=365)
                next_day = date + timedelta(days=10)
                prev_day = date - timedelta(days=10)
                new_date1 = date.strftime(date_format)
                new_date2 = next_day.strftime(date_format)
                data = yfinance.download(ticker,start=new_date1,end=new_date2)
                dowj_data = yfinance.download('SPY',start=new_date1,end=new_date2)

                counter = 0
                while data.empty:
                    if interrupted:
                        valid_line = False
                        i = 5
                        interrupted = False
                        break
                    next_day += timedelta(days=10)
                    prev_day -= timedelta(days=10)
                    new_date2 = next_day.strftime(date_format)
                    data = yfinance.download(ticker,start=new_date1,end=new_date2)
                    if data.empty:
                        new_date2 = prev_day.strftime(date_format)
                        data = yfinance.download(ticker,start=new_date2,end=new_date1)
                    if counter > 10:
                        break
                    counter += 1

                counter = 0


                while dowj_data.empty:
                    if interrupted:
                        valid_line = False
                        i = 5
                        interrupted = False
                        break
                    next_day += timedelta(days=10)
                    prev_day -= timedelta(days=10)
                    new_date2 = next_day.strftime(date_format)
                    dowj_data = yfinance.download("SPY",start=new_date1,end=new_date2)
                    if data.empty:
                        new_date2 = prev_day.strftime(date_format)
                        dowj_data = yfinance.download("SPY",start=new_date2,end=new_date1)
                    if counter > 10:
                        break
                    counter += 1
                    

                if valid_line:
                    close_data = data['Close'].head(1).to_string()
                    close_data = close_data.split()
                    dowj_close_data = dowj_data['Close'].head(1).to_string()
                    dowj_close_data = dowj_close_data.split()

                    value_list_4.append((current_price - float(close_data[2]))/current_price)
                    value_list_5.append((current_dowj_price - float(dowj_close_data[2]))/current_dowj_price)

            count += 1
            
            final_list = value_list_1 + value_list_2 + value_list_3 + value_list_4 + value_list_5
            final_list.append((float(y)-current_price)/current_price)

            if valid_line:
                writer.writerow(final_list)
            f.flush()
    except:
        print("Error occured.")

f.close()
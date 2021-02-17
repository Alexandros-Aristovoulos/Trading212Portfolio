import re
from forex_python.converter import CurrencyRates
from bs4 import BeautifulSoup as bs
import requests
from yahoo_fin import stock_info as si
import pandas as pd
from usefulFunctions import split_text

def makeStats(dfMail): 
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    #initialise the dataframes
    dfOrder = pd.DataFrame()

    #if there is an offset.csv get the data
    try:
        dfOrder = pd.read_csv("orders.csv")

        #drop useless columns
        dfOrder = dfOrder.drop(columns=['Name', 'Price / share', 'Currency (Price / share)', 'Exchange rate'])

        #split columns like in the email
        dfOrder[['Date','Time']] = dfOrder.Time.str.split(" ",expand=True)
        dfOrder[['Order Type','Direction']] = dfOrder.Action.str.split(" ",expand=True)

        #re-arrange the columns
        dfOrder = dfOrder.reindex(['Date', 'Time', 'ID', 'Ticker','ISIN', 'Order Type', 'Direction', 'No. of shares', 
                                     'Total (EUR)', 'Finra fee (EUR)', 'Stamp duty reserve tax (EUR)'], axis=1)

        #rename the columns
        dfOrder = dfOrder.rename(columns={"No. of shares": "Quantity", "Total (EUR)": "Total", 'Finra fee (EUR)': 'Commission', 
                                            'Stamp duty reserve tax (EUR)' : 'Charges and Fees', 'ID' : 'Id'})
        #capitalise Buy and Sell
        dfOrder['Direction'] = dfOrder['Direction'].str.capitalize()

        print("-----------------------------------------------Order Data-----------------------------------------------")
        print(dfOrder)
    except:
        #do nothing
        print("There is no orders csv")


 
    #if there are email data get them
    if not dfMail.empty:
        print("-----------------------------------------------Mail Data-----------------------------------------------")
        print(dfMail)
    else:
        print("No email Data")

    #combine all the data in one dataframe
    if((not dfOrder.empty) and (not dfMail.empty)):
        dfPortfolio = pd.concat([dfMail, dfOrder], axis=0, join='outer')
    elif(not dfOrder.empty):
        dfPortfolio = dfOrder
    elif(not dfMail.empty):
        dfPortfolio = dfMail
    else:
        #if you don't have any data return an empty dataFrame
        return pd.DataFrame()
    print("-----------------------------------------------Portfolio Data-----------------------------------------------")
    print(dfPortfolio)


    #initialise the titles for the stats arrays
    formattedPortfolio = [["Ticker", "ISIN", "Quantity", "Invested", "Average Price", "Withdrew", "LastClosedProfit", "Current Fees", "Total Fees"]]
    
    #group all the rows with same stock name

    groupTicker = dfPortfolio.groupby("Ticker")


    for ticker, group in groupTicker: 
        #stock is the name of the stock
        #we get isin from the grouped stocks
        isin = group["ISIN"].head(1).to_string(index=False).strip()

        #initialise variables 
        quantity = 0
        invested = 0
        withdrew = 0
        fees = 0
        totalFees = 0
        lastClosedProfit = 0

        #calculate their actual value by looping through the rows
        for _, row in group.iterrows():
            if row["Direction"] == "Buy":
                quantity += row["Quantity"]
                invested += row["Total"]

                #Fees (this is to check that it has a number -> it isn't NaN)
                if row["Commission"] == row["Commission"]:
                    fees += row["Commission"]
                if row["Charges and Fees"] == row["Charges and Fees"]:
                    fees += row["Charges and Fees"]

            else:
                quantity -= row["Quantity"]
                withdrew += row["Total"]

                #Fees (this is to check that it has a number -> it isn't NaN)
                if row["Commission"] == row["Commission"]:
                    fees += row["Commission"]
                if row["Charges and Fees"] == row["Charges and Fees"]:
                    fees += row["Charges and Fees"]
            
            #when quantity becomes == 0 then this position has beeen closed 
            if quantity == 0:
                #update last closed profit and reset everything else
                lastClosedProfit += withdrew - invested - fees
                invested = 0
                withdrew = 0
                fees = 0
                #totalFees variable tracks all th payed fees while the fees variable tracks the fees since
                #the last time the position was closed
                totalFees += fees

        #calculate current average Price (quantity must be >0)
        if quantity > 0:
            averagePrice = (invested + fees - withdrew)/ quantity
            averagePrice = round(averagePrice, 3)
        else:
            averagePrice =  float('nan')

        #add to the total fees the current fees
        totalFees += fees

        #remove fractions of a cent caused by the way computers store values
        invested = round(invested, 3)
        withdrew = round(withdrew, 3)
        lastClosedProfit = round(lastClosedProfit, 3)
        fees = round(fees, 4)
        totalFees = round(totalFees, 4)
        
        #add all the data to an array
        formattedPortfolio.append([ticker, isin, quantity, invested, averagePrice, withdrew, lastClosedProfit, fees, totalFees])

    print("-----------------------------------------------Formated Portfolio Data-----------------------------------------------")
    dfFormattedPortfolio = pd.DataFrame(data = formattedPortfolio[1:][0:],       # values
                                        columns = formattedPortfolio[0][0:])     # 1st row as the column names
    #drop rows where quantity == 0
    dfFormattedPortfolio = dfFormattedPortfolio[dfFormattedPortfolio["Quantity"] != 0]
    #reset the index
    dfFormattedPortfolio.reset_index(drop=True, inplace=True)
    print(dfFormattedPortfolio)
    return dfFormattedPortfolio

def yahooInfo(dfFormattedPortfolio):
    #get all the stock names
    isins = dfFormattedPortfolio["ISIN"].tolist()
    #get the number of share we have
    shares = (dfFormattedPortfolio["Quantity"]).tolist()
   
    #get currency rates to convert everything to euros
    print("Getting currency exchange rates")
    c = CurrencyRates()                                                 
    usdEurRate = c.get_rate('USD', 'EUR')
    gbpEurRate = c.get_rate('GBP', 'EUR')
    nokEurRate = c.get_rate('NOK', 'EUR')   

    #the list where all the stocks values (in euros) will be saved
    eurVal = []

    stocks = []

    #get the current value of each stock
    print("Getting the current value of each stock")
    for i in range(len(isins)): 
        try:

            #search in yahoo finance with the isin
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            params = {'q': isins[i], 'quotesCount': 1, 'newsCount': 0}
            r = requests.get(url, params=params)
            #get all the data for this isin
            data = r.json()
            #get the stock symbol for this isin
            symbol = data['quotes'][0]['symbol']

            #add the symbol to the stocks
            stocks.append(symbol)

            #get the current value of the stock in whatever currency
            curPrice = si.get_live_price(symbol) * shares[i]
           
            #get the currency the stock is traded in by going to that url
            url = "https://finance.yahoo.com/quote/"
            #get the html page of the stock
            r = requests.get(str(url+symbol))
            #get the html text
            soup = bs(r.text, "lxml")
            #find the div which contains the words "Currency in" and get the text
            currencyInfo = soup.find("div", string=re.compile("Currency in"))
            #get the currency (the word after the words "Currency in")
            currency = str(split_text(currencyInfo.text, "Currency in", "")) 

            #convert everything to euros if necessary
            if currency == "USD":
                curPrice = usdEurRate*curPrice
            elif currency == "GBp":
                curPrice = gbpEurRate*curPrice*0.01
            elif currency == "NOK":
                curPrice = nokEurRate*curPrice
            #save the value in euros in this list
            eurVal.append(round(curPrice, 2))
            
        #if the stock name doesn't exist in yahoo finance print error message
        except Exception as e:
            print(e)
            #assign the value in euros to NA (not available)
            eurVal.append(float("nan"))

    #get the value we have currently invested
    investedValue= (dfFormattedPortfolio["Invested"] - dfFormattedPortfolio["Withdrew"]).tolist()

    #this where we will store the temporary profit/loss
    tempProfit = [float("nan")] * len(isins)

    #remove from current value the total value currently invested
    for i in range(len(tempProfit)):
        if eurVal[i] == eurVal[i]:
            tempProfit[i] = eurVal[i] - investedValue[i]
    
    #append everything in this array
    liveStockData = [["Stock", "ISIN", "Quantity", "Average Price", "Invested Value", "Current Investment Value", "Profit"]]

    quantity = dfFormattedPortfolio["Quantity"].tolist()
    averagePrice = dfFormattedPortfolio["Average Price"].tolist()

    for i in range(len(stocks)):
        liveStockData.append([stocks[i], isins[i], quantity[i], averagePrice[i], investedValue[i], eurVal[i], tempProfit[i]])    

    print("-----------------------------------------------Current Positions' Value-----------------------------------------------")

    dfLivePositionValues = pd.DataFrame(data = liveStockData[1:][0:],       # values
                                        columns = liveStockData[0][0:])     # 1st row as the column names
    print(dfLivePositionValues)
    return dfLivePositionValues


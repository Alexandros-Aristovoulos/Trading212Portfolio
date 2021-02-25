import pandas as pd
import getStocksFromGmail
import stockAndCurrencyData
import allTheGraphs

GET_EMAIL = True
EXTRA_SEARCH_ARGS = "after:2021-02-14"
#choose the currency of your account (examples: EUR, USD, GBP, NOK)
#THIS IS CASE SENSITIVE
USER_CURRENCY = "EUR"

def main():
    #get all the info from gmail in an csv
    if GET_EMAIL:
        dfMail = getStocksFromGmail.getAllInfo(EXTRA_SEARCH_ARGS, USER_CURRENCY)
    else:
        dfMail = pd.DataFrame()

    #use the info to make statistics
    dfFormattedPortfolio = stockAndCurrencyData.makeStats(dfMail, USER_CURRENCY)

    #get the live data from yahoo and forex (only if you have data)
    if not dfFormattedPortfolio.empty:
        dfLivePositionValues = stockAndCurrencyData.yahooInfo(dfFormattedPortfolio, USER_CURRENCY)
        #graph everything
        allTheGraphs.graph(dfLivePositionValues)
    
if __name__ == '__main__':
    main()

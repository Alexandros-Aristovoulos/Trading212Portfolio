import pandas as pd
import getStocksFromGmail
import stockAndCurrencyData
import allTheGraphs

GET_EMAIL = False
EXTRA_SEARCH_ARGS = "after:2021-02-14"

def main():
    #get all the info from gmail in an csv
    if GET_EMAIL:
        dfMail = getStocksFromGmail.getAllInfo(EXTRA_SEARCH_ARGS)
    else:
        dfMail = pd.DataFrame()

    #use the info to make statistics
    dfFormattedPortfolio = stockAndCurrencyData.makeStats(dfMail)

    #get the live data from yahoo and forex (only if you have data)
    if not dfFormattedPortfolio.empty:
        dfLivePositionValues = stockAndCurrencyData.yahooInfo(dfFormattedPortfolio)
        #graph everything
        allTheGraphs.graph(dfLivePositionValues)
    
if __name__ == '__main__':
    main()

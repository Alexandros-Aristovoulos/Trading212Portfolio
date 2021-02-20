# Trading212Portfolio
### Description
The goal of this project is to get your Trading212 portfolio, calculate your returns and show everything in a graph without having to log in to the trading 212 website. 
This is achieved by getting the order information from a provided csv and/or the gmail of the user and searching in yahoo finance for the current price of the stock using the ISIN.

### Image example of script output
![](/example_output.png)

### Information
**This project is designed for accounts with EURO currency**. It converts Usd, GBp, and Nok to euro. You can add more conversions by adding a conversion variable in the
yahooInfo function. (dont forget to use it after the "convert everything to euros if necessary" comment) 

Place your (order data).csv which you can download from Trading212 
[(instructions here)](https://community.trading212.com/t/new-feature-export-your-investing-history/35612) **and selecting ONLY the orders as included data**.
You need to name this file as orders and replace my own file.

You can also use your gmail (if it receives the emails from Trading212) in order to automatically update the orders data. Beware my script only gets the data
from the "Contract Note Statement from Trading 212" so if you are informed about an order via the "Monthly statement" the code won't know anything about it.

**Change the variables GET_EMAIL and EXTRA_SEARCH_ARGS in the myPortfolio.py accordingly.**

### Updates
Changed the logic we use to find the stocks and get their price. 
* First we search for the stock in the London stock exchange because that's the exchange Trading212 "prefers". To do that we just add ".L" at the end of the stock name. 
* If we don't find the stock this way then we try with the original name. (That's how we find most of the US stocks)
* If none of the above work then we use the isin and get the first ticker that matches it. Then using that ticker we get the price. (That's how we find stocks in other
exchanges) 

### Dependencies
- Gmail api (follow the steps 1 and 2 from [here](https://developers.google.com/gmail/api/quickstart/python) and add the credentials.json in the project folder)
- [Email](https://pypi.org/project/email/)
- [Pandas](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)
- [BeautifulSoup 4](https://pypi.org/project/beautifulsoup4/)
- [Requests](https://pypi.org/project/requests/)
- [Yahoo finance](https://pypi.org/project/yahoo-fin/)
- [Forex python](https://pypi.org/project/forex-python/)
- [Numpy](https://numpy.org/install/)
- [Matplotlib](https://pypi.org/project/matplotlib/)

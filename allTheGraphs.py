import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
from forex_python.converter import CurrencyRates


def graph(dfLivePositionValues):
    ############Invested money pie chart###############

    #get the stock names
    stocks = dfLivePositionValues["Stock"].tolist()
    #get the invested money
    totalVal = dfLivePositionValues["Invested Value"].tolist()
    
    fig1, ((ax1, ax4), (ax3, ax2)) = plt.subplots(2, 2)
    wedges, texts = ax1.pie(totalVal, shadow=False, frame=False, wedgeprops={'linewidth':1, 'edgecolor':"white"}, startangle=90)
    # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.axis('equal')  
    #the title of this pie
    ax1.set_title("Money Invested")   

    #This does the cool annotations
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1

        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))

        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})

        percentage = "{:.2f}".format(100*totalVal[i]/sum(totalVal))
        percentage = str(percentage) + "%"
        ax1.annotate(str(totalVal[i])+"€\n"+percentage, xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, **kw)

    ax1.legend(wedges, stocks, title ="Stocks", loc ="best") 
    ###############End of invested money pie chart###################
    
    
    ###############Currency rates bar chart######################
    #get the currency rates
    c = CurrencyRates()                                                 
    eurUsdRate = c.get_rate('EUR', 'USD')
    eurGbpRate = c.get_rate('EUR', 'GBP')
    eurNokRate = c.get_rate('EUR', 'NOK')
    
    currencies = ('Euro/Usd', 'Euro/Gbp', 'Euro/NOK')
    y_pos = np.arange(len(currencies))
    rates = [round(eurUsdRate, 3), round(eurGbpRate, 3), round(eurNokRate, 3)]   
    
    #graph the horizontal bar chart
    ax2.barh(y_pos, rates, align='center')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(currencies)
    ax2.set_title('Currency Rates')

    #have the actual value next to each bar
    for i, v in enumerate(rates):
        ax2.text(v, i, " "+str(v), color='black', va='center')

    #remove the borders
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    #################End of currency rates bar chart##############


    #################Profit/Loss bar chart################
    profits = (round((dfLivePositionValues["Profit"]), 2)).tolist()
    
    x_pos = np.arange(len(stocks))

    #get the colors
    col = []
    for val in profits:
        if val < 0:
            col.append('red')
        elif val > 0:
            col.append('green')
        else:
            col.append('blue')   
    
    #add the names and values
    ax3.bar(x_pos, profits, align='center', color = col)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(stocks)
    ax3.set_title('Profit/Loss')

    #add the actual value next to the bar
    for i, v in enumerate(profits):
        if v>0:
            ax3.text(i, v + 0.25, str(v), color='black', ha='center')
        else:
            ax3.text(i, v - 0.5, str(v), color='black', ha='center')

    #remove the borders
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['bottom'].set_visible(False)
    ax3.spines['left'].set_visible(False)
    ############End of Profit/Loss bar chart######################


    #############Current invested value pie chart#####################
    
    #get the stock names
    stocks = dfLivePositionValues["Stock"].tolist()
    #get the invested money
    totalVal = dfLivePositionValues["Current Investment Value"].tolist()
    
    wedges, texts = ax4.pie(totalVal, shadow=False, frame=False, wedgeprops={'linewidth':1, 'edgecolor':"white"}, startangle=90)
    #Equal aspect ratio ensures that pie is drawn as a circle.
    ax4.axis('equal')  
    #the title of this pie
    ax4.set_title("Current Stock Value")   

    #This does the cool annotations
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1

        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))

        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})

        percentage = "{:.2f}".format(100*totalVal[i]/sum(totalVal))
        percentage = str(percentage) + "%"
        ax4.annotate(str(totalVal[i])+"€\n"+percentage, xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, **kw)


    ax4.legend(wedges, stocks, title ="Stocks", loc ="best") 
    ###########End of invested money pie chart#####################
    
    #maximise window
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
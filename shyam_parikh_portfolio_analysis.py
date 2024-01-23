# Name:Shyam Parikh

# You may not import any additional libraries for this challenge besides the following
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import yfinance as yf

class PortfolioAnalysis:
    
    """
    Create a constructor that reads in the excel file and calls all necessary methods
    You may set the output of these methods to be attributes of the class that you may
    access later on in other challenges.

    Create a method called `clean_data` which accurately deals with any discrepancies
    in the input data and returns usable data that you can access for the rest of your tasks
    You must have comments explaining why you chose to make any of the changes you did. Any
    missing (NA) values must be calculated for or found from yfinance accordingly.
    The cleaned data should be exported to an excel file with 3 sheets, all of the same format
    as the original data. The file name should be called `cleaned_data.xlsx`.
    
    #NOTE:
    You may import and use this cleaned data file for any of the optional challenges, as needed.
    You may also import this file and create an instance of the PortfolioAnalysis class to use
    in any of the optional challenges, as needed.

    Create a method called `asset_value` that calculates the total market value of each equity
    in the portfolio at the end of the month, with tickers in the rows and dates in the columns
    as well as another row that keeps track of the portfolio's Net Asset Value (NAV) at the end
    of each month. If there is no position for a certain equity during a given month, its value
    should be 0. This data should be kept track of from the end of June to the end of September

    Create a method called `unrealized_returns` that calculates the unrealized returns of each stock.
    The output should be a dataframe that has tickers in the rows, dates in the columns, and the
    unrealized gain/loss of each ticker at the end of each month.
    If there is no unrealized loss to be calculated for a given stock during a given month, its
    value should be 0.

    Create a method called `plot_portfolio` that builds a plot of the portfolio's value over time,
    from the end of June to the end of September

    Create a method called `plot_liquidity` that builds a plot of the ratio between the cash on
    hand and the portfolio's total value, from the end of June to the end of September
    """
    #TODO delete the following line and start building the PortfolioAnalysis class.
    pass

    def __init__(self,excel:pd.DataFrame):
        self.data = pd.concat(pd.read_excel(excel,sheet_name= None),ignore_index =False)
        self.cleaned_data = self.clean_data()
        self.asset_values = self.asset_value()
        self.unrealized_pnl = self.unrealized_returns()
    def clean_data(self) -> pd.DataFrame:
        #########################################################################
        ## 1st Part 
        ## Organizing the sheets by adding Date as an Index
        #########################################################################
        df = self.data.reset_index()
        df['Date'] = df['level_0']
        df = df.drop(["level_0","level_1"],axis=1)
        #########################################################################
        ## 2nd Part 
        ## Filling NA VALUES for UnitCost Column and MarketPriceCOlumn
        ## Converting String Types into Float Types for Unit Cost column and Market
        ## Price Column
        ##Used Stack to find Index of Element
        #########################################################################
        ## iterating through pandas dataframe
        for index, row in df.iterrows():
            ## Checking to see if there is NaN value in a specific row in the 'MarketPrice' Column
            if pd.isna(row['MarketPrice']):
                ticker = row['Stock']
                date = row['Date']
                stock = yf.Ticker(ticker)
                stock_data = stock.history(start= df['Date'][0], end= date)['Close'][-1]
                df.at[index, 'MarketPrice'] = stock_data 
            ## Checking to see if there is NaN value in a specific row in the 'UnitCost' Column
            if pd.isna(row['UnitCost']):
                ticker = row['Stock']   
                newDF = df.loc[(df["Stock"] == ticker)]
                val = np.mean(newDF['UnitCost'])
                df.at[index, 'UnitCost'] = val 
            ## Checking to see if a specific value in the UnitCost column is a string
            if isinstance(row['UnitCost'],str):
                s = float(row['UnitCost'].replace('"',''))
                df.at[index, 'UnitCost'] = s 
            ## Checking to see if a specific value in the MarketPrice column is a string
            if isinstance(row['MarketPrice'],str):
                s = float(row['MarketPrice'].replace('"',''))
                df.at[index, 'MarketPrice'] = s 
        ## For me, I am saving the cleaned_data as an excel file, but I would 
        ## rather have all of the data in one excel sheet so I am returning a
        ## dataframe with all of the data. 
        uniqueDates = []
        with pd.ExcelWriter('cleaned_data.xlsx') as writer:  
            for x in df['Date']:
                if x not in uniqueDates:
                    uniqueDates.append(x)    
                    exportedDf= df.loc[(df["Date"] == x)]
                    exportedDf = exportedDf.reset_index()
                    exportedDf = exportedDf.drop(["Date","index"],axis=1)
                    exportedDf.to_excel(writer,sheet_name=x)
                
        ## Returning dataframe in format that 
        return df 
    ########################################################################
    ## Using Cleaned Data and then multiplying quantity by the market price 
    ## to find the total asset value for each equity at the end of each month
    ## For the initial value, I ust multiplied the Quantity by the Unit Cost 
    ########################################################################
    def asset_value(self) -> pd.DataFrame:
        df = self.cleaned_data
        ## Gathering All of the Stocks and Dates tracked without having any repeats
        uniqueDates = []
        for x in df['Date']:
            if x not in uniqueDates:
                uniqueDates.append(x)
        stocks = []
        for x in df['Stock']:
            if x not in stocks:
                stocks.append(x)
        stocks.append("NAV(Net Asset Value)")
        columns = {"Stock":stocks}
        vals = []
        for i in range(len(uniqueDates)):
            newDF = df.loc[(df["Date"] == uniqueDates[i])]
            newDF = newDF.reset_index()
            assetVal = [] 
            for x in range(len(stocks)-1):
                ## Following if and try,except statement represents the case of calculating the 
                ## asset value for the initial date in the portfolio
                if (i == 0):
                    try:
                        ind = newDF.loc[(newDF["Stock"] == stocks[x])].index
                        vals.append(newDF['Quantity'][ind[0]] * newDF['UnitCost'][ind[0]])
                    except:
                        vals.append(0)
                    if x == (len(stocks)-2):
                        vals.append(sum(vals))
                    ##Manually Entered Time for June, since not mentioned in the dataframe
                    columns["2023-06-30"] = vals    
                stockList = list(newDF['Stock'])
                if(stocks[x] in stockList):
                    ind = newDF.loc[(newDF["Stock"] == stocks[x])].index
                    ## Represents the Asset Value of each stock
                    assetVal.append(newDF['Quantity'][ind[0]] * newDF['MarketPrice'][ind[0]])
                else:
                    assetVal.append(0)
            ## Represents total Net Asset Value of the portfolio by taking the sum of all the
            ## assetVal rows
            assetVal.append(sum(assetVal))
            columns[uniqueDates[i]] = assetVal
        assetValueDf = pd.DataFrame(columns)
        assetValueDf
        return assetValueDf
    ########################################################################
    ## Using Cleaned Data and Similar Code from asset_value().
    ## Only major difference is instead of Asset Value, I am simply finding the
    ## the difference of the asset value after each month. 
    ########################################################################
    def unrealized_returns(self) ->pd.DataFrame:
        ## Cleaning the data and gathering the unique Dates and Stocks that are not repeats
        ## in the dataframe
        df = self.cleaned_data
        uniqueDates = []
        for x in df['Date']:
            if x not in uniqueDates:
                uniqueDates.append(x)
        stocks = []
        for x in df['Stock']:
            if x not in stocks:
                stocks.append(x)
        stocks.append("Total Unrealized Gains/Losses")
        columns = {"Stock":stocks}
        ## Following array is used to represent the values at the beginning date. 
        vals = []
        ## Iterates through all of the dates in the dataframe
        for i in range(len(uniqueDates)):
            newDF = df.loc[(df["Date"] == uniqueDates[i])]
            newDF = newDF.reset_index()
            unrealizedReturns = [] 
            for x in range(len(stocks)-1):
                ## Checks specifically for the month of June
                if (i == 0):
                    vals.append(0)
                    if x == (len(stocks)-2):
                        vals.append(sum(vals))
                        ##Manually Entered Time for June, since not mentioned in the dataframe
                        columns["2023-06-30"] = vals    
                stockList = list(newDF['Stock'])
                ## Finding the index of the stock in the dataframe and calculating the total unrealized gains and losses of a specific stock
                if(stocks[x] in stockList):
                    ind = newDF.loc[(newDF["Stock"] == stocks[x])].index
                    unrealizedReturns.append((newDF['Quantity'][ind[0]] * newDF['MarketPrice'][ind[0]])-newDF['Quantity'][ind[0]] * newDF['UnitCost'][ind[0]])
                else:
                    unrealizedReturns.append(0)
            unrealizedReturns.append(sum(unrealizedReturns))
            columns[uniqueDates[i]] = unrealizedReturns
        unrealizedReturnsDF = pd.DataFrame(columns)
        return unrealizedReturnsDF


    ########################################################################
    ##Using Matplotlib to plot graph of the portfolio performance over time
    ########################################################################
    def plot_portfolio(self):
        df = self.asset_values
        x = df.columns[1:]
        y = df.iloc[-1][1:].values
        plt.plot(x,y)
        plt.title("Total Portfolio Value")
        plt.xlabel("Date")
        plt.ylabel("$Portfolio Value(US Dollars)")
        plt.show()

    ########################################################################
    ##Calculuating the Liquidity Ratio from the dataframe and then using
    ##  Matplotlib to plot graph of the portfolio performance over time 
    ########################################################################
    def plot_liquidity(self):
        df = self.asset_values
        x = df.columns[1:]
        ind = df.loc[(df["Stock"] == "Cash")].index
        y = (df.iloc[ind[0]][1:].values) / (df.iloc[-1][1:].values)
        plt.plot(x,y)
        plt.title("Portfolio Liquidity")
        plt.xlabel("Date")
        plt.ylabel("Liquidity Ratio")
        plt.show()

if __name__ == "__main__":  # Do not change anything here - this is how we will test your class as well.
    fake_port = PortfolioAnalysis("dummy_data.xlsx")
    print(fake_port.asset_values)
    print(fake_port.unrealized_pnl)
    fake_port.plot_portfolio()
    fake_port.plot_liquidity()
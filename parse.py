import csv
import imp
import pandas as pd
import numpy as np
import datetime
import operator
import math
from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta, date, time


class Order:
    def cost(self):
        price = self.Price
        qty = self.Qty
        orderCost = price*qty *-1
        return(round(orderCost, 2))

class Ticker:
    def __init__(self, symbol, orders):
        self.Symbol = symbol
        self.Orders = orders
    def totalOrders(self):
        total = 0
        for order in self.Orders:
            total += 1
        return(total)
    def totalPnL(self):
        total = 0
        for order in self.Orders:
            total += order.cost()
        return(total)

class Trade:
    def __init__(self, symbol, orders):
        self.Symbol = symbol
        self.Orders = orders



rowsToSkip = 0
filename = '2022-07-21-AccountStatement.csv'
start_dt = date(2022, 7, 21)
end_dt = date(2022, 7, 21)


with open(filename,'rt')as f:
  data = csv.reader(f)
  count = 0
  for row in data:
      count += 1
      for field in row:
          if field == 'Account Trade History':
              rowsToSkip = count

data = pd.read_csv(filename, skiprows=rowsToSkip)

df = pd.DataFrame(data)

stocks = df[df.Type == 'STOCK']
buys = stocks[stocks.Side == 'BUY']
sells = stocks[stocks.Side == 'SELL']
filledOrders = buys.append(sells)

orderRecs = []
orderRecords = filledOrders.to_records()
for record in orderRecords:
    order = Order()
    order.Price = float(record.Price)
    order.Qty = int(record.Qty)
    order.ExecTime = datetime.datetime.strptime(str(record['Exec Time']), '%m/%d/%y %H:%M:%S')
    order.Symbol = str(record.Symbol)
    order.Side = str(record.Side)
    # ********                                              **********
    # ********        GET ENTRY PRICE   &   EXIT PRICES     **********
    # ********                                              **********
    # print(record)
    orderRecs.append(order)


sortedOrders = sorted(orderRecs, key=operator.attrgetter('ExecTime'))


def getTickersForOrders(orders):
    symbols = []
    tickers = []
    for order in orders:        
        if order.Symbol not in symbols:
            symbols.append(order.Symbol)
            orderList = []
            orderList.append(order)
            ticker = Ticker(order.Symbol, orderList)
            tickers.append(ticker)
        else:
            ticker = [ticker for ticker in tickers if ticker.Symbol == order.Symbol][0]
            ticker.Orders.append(order)
    return(tickers)


def printAllOrders(orders):
    for order in orders:
        print('Time: ' + str(order.ExecTime)
            + ' Symbol: ' + str(order.Symbol)
            + ' Cost: ' + str(order.cost())
            + ' Side: ' + str(order.Side)
            + ' Price: ' + str(order.Price)
            + ' Qty: ' + str(order.Qty))


def printAllTickers(tickers):
    for ticker in tickers:
        print('Ticker: ' + str(ticker.Symbol)
            + '     Total Orders: ' + str(ticker.totalOrders())
            + '     Total PnL: ' + str(ticker.totalPnL()))


def getTotalForTickers(tickers):
    totalProfits = 0
    for ticker in tickers:
        totalProfits += ticker.totalPnL()
    return totalProfits


def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)


def getDatesInDateRange(start, end):
    days = []
    for dt in daterange(start, end):
        days.append(dt.strftime("%Y-%m-%d"))
    return(days)


def getOrdersForDateRange(startDate, endDate):
    orders = [order for order in sortedOrders if order.ExecTime.date() >= startDate and order.ExecTime.date() <= endDate]
    return orders


def getOrdersForDate(date):
    orders = [order for order in sortedOrders if order.ExecTime.date() == date]
    return orders


def getPnLForDate(date):
    ordersForDate = getOrdersForDate(date)
    tickersForDate = getTickersForOrders(ordersForDate)
    return getTotalForTickers(tickersForDate)


def getPnLForDateRange(startDate, endDate):
    ordersForDateRange = getOrdersForDateRange(startDate, endDate)
    tickersForDateRange = getTickersForOrders(ordersForDateRange)
    return getTotalForTickers(tickersForDateRange)


def printPnLForDateRange(startDate, endDate):
    dates = getDatesInDateRange(startDate, endDate)
    for dateString in dates:
        date = datetime.datetime.strptime(dateString, '%Y-%m-%d').date()
        pnl = getPnLForDate(date)
        print(dateString + ': ' + str(pnl))



# start_dt = date(2020, 2, 3)
# end_dt = date(2020, 2, 8)


orders = getOrdersForDateRange(start_dt, end_dt)

tickersHere = getTickersForOrders(orders)
trades = []
pnl = 0

for ticker in tickersHere:
    orderQty = 0
    tradeCount = 0
    orderCount = 0
    orderIndex = 0
    openBuyingPower = 0
    totalBuyingPower = 0
    highestOpenBP = 0
    sells = 0
    buys = 0
    transactionFees = 0
    highestExitPrice = 0
    lowestEntryPrice = 1000
    for order in ticker.Orders:        
        pnl += order.cost()
        if order.cost() < 0:
            orderAmount = order.cost() * -1
            transactionFees += orderAmount                  
            openBuyingPower += orderAmount
            print("added some " + str(ticker.Symbol) + ": " + str(order.Qty) + " * " + str(order.Price) + "= " + str(round(order.cost()*-1, 2)) + " open bp: " + str(round(openBuyingPower, 2)))                        
            if order.Price < lowestEntryPrice:
                lowestEntryPrice = order.Price
            if openBuyingPower > highestOpenBP:
                highestOpenBP = openBuyingPower
            totalBuyingPower += openBuyingPower            
            if order.Price > highestExitPrice:
                highestExitPrice = order.Price
        else:
            orderAmount = order.cost()
            transactionFees += orderAmount            
            openBuyingPower -= orderAmount
            print("sold some " + str(ticker.Symbol) + ": " + str(order.Qty) + " * " + str(order.Price) + "= " + str(round(order.cost()*-1, 2)) + " open bp: " + str(round(openBuyingPower,2 )))            
            currentExit = (order.Price)
            if order.Price < lowestEntryPrice:
                lowestEntryPrice = order.Price
            if currentExit > highestExitPrice:
                highestExitPrice = currentExit
            
        
        orderCount += 1
        orderIndex += 1
        fees = 0
        if order.Qty < 0:                
            qty = order.Qty * -1
            # fees = qty * 0.00013333
            fees = 0
        # section31Fees = transactionFees*0.0000207
        # fees += section31Fees
        orderQty += order.Qty
        if orderQty == 0:            
            print("exited trade")
            print("highest open bp: " + str(highestOpenBP)) 
            print("lowest entry price: " + str(lowestEntryPrice))               
            print("highest exit price : " + str(highestExitPrice))         
            tradeCount += 1
            if tradeCount > 1:                        
                # print(str(order.Symbol) + ' Order Count: ' + str(orderCount) + ' Trade Number: ' + str(tradeCount) + ' Trade PnL: ' + str(pnl))
                indexOrders = ticker.Orders[orderIndex-orderCount:orderIndex]
                trade = Trade(ticker.Symbol, indexOrders)
                # print("Entry: " + str(trade.Orders[0].Price) + " Exit: " + str(trade.Orders[-1].Price))
                trade.entryPrice = trade.Orders[0].Price
                trade.exitPrice = trade.Orders[-1].Price

                trade.timeStarted = trade.Orders[0].ExecTime
                trade.timeEnded = trade.Orders[-1].ExecTime
                trade.fees = fees
                trade.highestOpenBP = highestOpenBP
                trade.lowestEntryPrice = lowestEntryPrice
                trade.highestExitPrice = highestExitPrice
                highestOpenBP = 0
                highestExitPrice = 0
                # print('Trade Fees: ' + str(fees))
                trades.append(trade)
            else:                
                # print(str(order.Symbol) + ' Order Count: ' + str(orderCount) + ' Trade Number: ' + str(tradeCount) + ' Trade PnL: ' + str(pnl))
                indexOrders = ticker.Orders[0:orderCount]
                trade = Trade(ticker.Symbol, indexOrders)
                trade.entryPrice = trade.Orders[0].Price
                trade.exitPrice = trade.Orders[-1].Price

                trade.timeStarted = trade.Orders[0].ExecTime
                trade.timeEnded = trade.Orders[-1].ExecTime
                trade.fees = fees
                trade.highestOpenBP = highestOpenBP
                trade.lowestEntryPrice = lowestEntryPrice
                trade.highestExitPrice = highestExitPrice            
                highestOpenBP = 0
                highestExitPrice = 0
                # print('Trade Fees: ' + str(fees))
                trades.append(trade)

            pnl = 0
            orderCount = 0




sortedTrades = sorted(trades, key=operator.attrgetter('timeStarted'))
totalPercent = 0
totalDayPercent = 0
totalBPUsed = 0

for trade in sortedTrades:
    orderCount = 0
    total = 0
    bpUsed = 0
    totalPercent = 0
    transactionsUsed = 0
    totalTime = round((trade.timeEnded-trade.timeStarted).total_seconds()/60.0, 2)
    timeStarted = trade.timeStarted
    hour = trade.timeStarted.hour
    minute = trade.timeStarted.minute
    second = trade.timeStarted.second
    timeEnded = trade.timeEnded
    dateStarted = trade.timeStarted.date()
    ################################################
    # CALCULATE AVG LENGTH IN A TRADE
    ################################################
    testing = 0
    for order in trade.Orders:
        orderCount += 1        
        total += order.cost()

        if order.Side == 'BUY':
            bpUsed += order.cost()
            testing = bpUsed
            
            # print("Buy for amound: " + str(order.cost() *-1))
            transactionsUsed += 1
        else:
            # print("sell for amound: " + str(order.cost() *-1))
            testing -= order.cost()

            transactionsUsed += 1            
        # else:
        #     bpUsed -= (order.cost()*-1)
       # if order.cost() > 0:
       #      bpUsed += order.cost()
    
    trade.bpUsed = bpUsed
    trade.transactionsUsed = transactionsUsed

    

    if total < 0:
        trade.side = 'Loss'        
    else:
        trade.side = 'Win'
        

    # Round deciaml to two places:
    total = Decimal(total).quantize(Decimal("1.00"))
    

    trade.pnl = total

    if trade.highestOpenBP != 0:
        pnlPercent = round((float(total)/float(trade.highestOpenBP) * 100), 2)
    else:
        pnlPercent = 0
    
    totalDayPercent += pnlPercent
    totalBPUsed += bpUsed

    # if pnlPercent > 1.5 or pnlPercent < -1.5:
    print(str(trade.Symbol)
        + ' ' + trade.side + ', '   
        + str(trade.timeStarted.hour) + ":"
        + str(trade.timeStarted.minute) + ":"
        + str(trade.timeStarted.second)            
        + ' to '
        + str(trade.timeEnded.hour) + ":"
        + str(trade.timeEnded.minute) + ":"
        + str(trade.timeEnded.second)          
        + ', FirstEn: '
        + str(round(trade.entryPrice, 2))
        + ', LowestEn: '
        + str(round(trade.lowestEntryPrice, 2))
        + ', HighestEx: '
        + str(trade.highestExitPrice)
        + ', HExP: '
        + str(round((trade.highestExitPrice-trade.entryPrice)/trade.entryPrice*100, 2)) + "%"                
        + ', Length: '
        + str(totalTime)
        + ' Min.'
        + ', Executions: ' + str(trade.transactionsUsed)
        + ', PnL: $' + str(total)
        + ', HBP: $' + str(round(trade.highestOpenBP,2))
        + ' PnL %: ' + str(pnlPercent) + '%')

    
    


days = getDatesInDateRange(start_dt, end_dt)


totalWins = 0
totalLosses = 0
totalProfits = 0
totalFees = 0
dayCount = 0
print(' ')
print('-------------------')
print('Trading Results')
print('-------------------')
for day in days:
    totalPnL = 0    
    date = datetime.datetime.strptime(day, '%Y-%m-%d').date()
    trades = [trade for trade in sortedTrades if trade.timeEnded.date() == date]
    for trade in trades:
        totalPnL += trade.pnl
        totalFees += trade.fees
        if trade.side == 'Win':
            totalWins += 1
        else:
            totalLosses += 1
    if totalPnL != 0:
        print(str(day) + ': $' + str(totalPnL))
        totalWithFees = totalPnL - totalFees
        totalProfits += totalWithFees
        dayCount += 1

if totalProfits > -100000:   
    totalTrades = totalWins + totalLosses
    winFraction = float(totalWins)/float(totalTrades)
    winPercent =  Decimal(winFraction*100).quantize(Decimal("1.00"))
    avgBPPerTrade = (totalBPUsed/totalTrades) * -1
    actualPercent = float(totalProfits)/float(avgBPPerTrade)
    avgPercentPerTrade = float(actualPercent)/float(totalTrades)
    print(' ')
    print('Total: $' + str(totalProfits))
    print(' ')
    print('Wins: ' + str(totalWins))
    print('Losses: ' + str(totalLosses))    
    print('Winner Accuracy: ' + str(totalWins) + '/' + str(totalTrades) + ' = ' + str(winPercent) + '%')
    print('Average PnL/Day: ' + str(Decimal(totalProfits/dayCount).quantize(Decimal("1.00"))))        
    print(' ')
    # print('Total Percent: ' + str(totalDayPercent) + '%')
    print('Average BP Used: $' + str(round(avgBPPerTrade, 2)))    
    print(' ')
    # print('Average Percent Per Trade: %' + str(avgPercentPerTrade))
    # print(' ')    
    print('Return Based on BP: ')
    print('$' + str(totalProfits) + ' / ' + '$' + str(round(avgBPPerTrade, 2)) + ' = ' + str(round(actualPercent, 2)*100) + '%')
    # print('Actual Percent Return: ' + str(round(actualPercent, 2)*100) + '%')
    # print('Total BP Used: $' + str(totalBPUsed *-1))

    
    # print(' ')
    # print(' ')
    # testArray = [1.615, 1.615, 1.645, 1.715, 1.615]    
    # for num in testArray:
    #     print(Decimal(num).quantize(Decimal("1.00")))
    #     print(round(num, 2))
    #     print(num)

    
    


    # print('Profits: ' + str(totalProfits) + ' Fees: ' + str(totalFees))
else:
    print('Losses: ' + str(totalProfits))
    # print('Losses: ' + str(totalProfits)  + ' Fees: ' + str(totalFees))





#

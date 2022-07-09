import csv
import pandas
import datetime
import operator
from datetime import timedelta, date, time


class Order:
    def cost(self):
        price = self.Price
        qty = self.Qty
        return(price*qty *-1)

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
filename = '2-29-2020.csv'
start_dt = date(2020, 2, 1)
end_dt = date(2020, 2, 28)


with open(filename,'rt')as f:
  data = csv.reader(f)
  count = 0
  for row in data:
      count += 1
      for field in row:
          if field == 'Account Trade History':
              rowsToSkip = count

data = pandas.read_csv(filename, skiprows=rowsToSkip)

df = pandas.DataFrame(data)

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
    sells = 0
    buys = 0
    transactionFees = 0
    for order in ticker.Orders:
        pnl += order.cost()
        if order.cost() < 0:
            orderAmount = order.cost() * -1
            transactionFees += orderAmount
        else:
            orderAmount = order.cost()
            transactionFees += orderAmount
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
            tradeCount += 1
            if tradeCount > 1:
                # print(str(order.Symbol) + ' Order Count: ' + str(orderCount) + ' Trade Number: ' + str(tradeCount) + ' Trade PnL: ' + str(pnl))
                indexOrders = ticker.Orders[orderIndex-orderCount:orderIndex]
                trade = Trade(ticker.Symbol, indexOrders)
                trade.timeStarted = trade.Orders[0].ExecTime
                trade.timeEnded = trade.Orders[-1].ExecTime
                trade.fees = fees
                print('Trade Fees: ' + str(fees))
                trades.append(trade)
            else:
                # print(str(order.Symbol) + ' Order Count: ' + str(orderCount) + ' Trade Number: ' + str(tradeCount) + ' Trade PnL: ' + str(pnl))
                indexOrders = ticker.Orders[0:orderCount]
                trade = Trade(ticker.Symbol, indexOrders)
                trade.timeStarted = trade.Orders[0].ExecTime
                trade.timeEnded = trade.Orders[-1].ExecTime
                trade.fees = fees
                print('Trade Fees: ' + str(fees))
                trades.append(trade)

            pnl = 0
            orderCount = 0




sortedTrades = sorted(trades, key=operator.attrgetter('timeStarted'))

for trade in sortedTrades:
    orderCount = 0
    total = 0
    totalTime = (trade.timeEnded-trade.timeStarted).total_seconds()
    timeStarted = trade.timeStarted
    hour = trade.timeStarted.hour
    minute = trade.timeStarted.minute
    second = trade.timeStarted.second
    timeEnded = trade.timeEnded
    dateStarted = trade.timeStarted.date()

    for order in trade.Orders:
        orderCount += 1
        total += order.cost()

    if total < 0:
        trade.side = 'Loss'
    else:
        trade.side = 'Win'

    trade.pnl = total

    print(str(trade.Symbol)
        + ' ' + trade.side
        + ' Entry: '
        + str(trade.timeStarted)
        + ' Exit: '
        + str(trade.timeEnded)
        + ' Length: '
        + str(totalTime)
        + ' Seconds '
        + ' Orders: ' + str(orderCount)
        + ' PnL: $' + str(total))

days = getDatesInDateRange(start_dt, end_dt)

totalProfits = 0
totalFees = 0
for day in days:
    totalPnL = 0
    date = datetime.datetime.strptime(day, '%Y-%m-%d').date()
    trades = [trade for trade in sortedTrades if trade.timeEnded.date() == date]
    for trade in trades:
        totalPnL += trade.pnl
        totalFees += trade.fees
    print(str(day) + ' PnL: ' + str(totalPnL))
    totalWithFees = totalPnL - totalFees
    totalProfits += totalWithFees
if totalProfits > 0:
    print('Profits: ' + str(totalProfits) + ' Fees: ' + str(totalFees))
else:
    print('Losses: ' + str(totalProfits)  + ' Fees: ' + str(totalFees))




#

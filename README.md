# Yahoo Finance to CSV
A tiny Yahoo Finance API that lets you retrieve realtime and historical ~~(not yet)~~ stock data

# Installation:
```sh
git clone https://github.com/andportnoy/yahoo-finance-csv
```

# Usage:
``` python
import yfc  

# takes a list of tickers or a path to a csv file with a 'ticker' header
df1 = yfc.current(['AAPL', 'YHOO', 'GOOG'])

# takes one ticker
df2 = yfc.historical('COP')

# takes a list of tickers or a path to a csv file with a 'ticker' header
corrmat = yfc.correlation_matrix('tickers.csv')
```

You can visualize the correlation matrix using [seaborn](https://stanford.edu/~mwaskom/software/seaborn/examples/network_correlations.html).

# Development goals
Provide two main functions:  
1. `current`, delivering realtime stock data as fast as possible (as of now, it returns a pandas DataFrame, which is slower than raw data; the end user might prefer a different format)  
2. `historical`, exporting historical price data as a clean Pandas DataFrame

# To-dos:
- [ ] add tests
- [ ] add documentation
- [x] add `historical`
- [ ] see if using [YQL](https://github.com/lukaszbanasiak/yahoo-finance/blob/master/yahoo_finance/yql.py) is faster
- [x] add pandas capabilities (option to return a pandas dataframe)
- [x] handle N/A values for data (using pandas)
- [ ] parse numeric values that can't be converted using `pd.to_numeric` (e.g. EBITDA with letters M, B for million and billion)
- [ ] add graphing capabilities (matplotlib or seaborn)

# Museum

Insane one-liner (not used in the actual code) that cleans the data and computer a correlation matrix for a list of tickers with lambda functions, zip, map, filter, reduce, and listcomps inside:  
```python
reduce(lambda df1, df2: df1.join(df2, how='inner'), [df[['Close']].rename(columns={'Close': ticker}) for ticker, df in filter(lambda (ticker, df): df is not None, zip(ticker_list, map(historical, ticker_list)))]).corr()
```
## Steps:  
1. Retrieve historical data for each ticker in `ticker_list` using `map()`.
2. Create a list of 2-tuples with ticker and corresponding dataframe inside using `zip()`.
3. Filter the list, preserving only the tuples where the dataframe `is not None` using `filter()` and a `lambda` expression.
4. For each dataframe, drop all the columns except 'Close', put them in a list, using a list comprehension.
5. Rename the 'Close' column of each dataframe with the corresponding ticker using a dataframe method.
6. Inner-join the first two dataframes, then inner-join the result with the third dataframe, and so on, inner-joing all the dataframes using `reduce()` and a `lambda` expression

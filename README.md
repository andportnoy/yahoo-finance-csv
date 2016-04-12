# Yahoo Finance to CSV
A tiny Yahoo Finance API that lets you retrieve realtime and historical ~~(not yet)~~ stock data

# Development goals
Provide two main functions:  
1. `current`, delivering realtime stock data as fast as possible  
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

Insane one-liner that computes a correlation matrix for a list of tickers with lambda, zip, map, reduce, and listcomps inside:  
```python
return reduce(lambda df1, df2: df1.join(df2, how='inner'), [df[['Close']].rename(columns={'Close': ticker}) for ticker, df in zip(ticker_list, map(historical, ticker_list))]).corr()
```

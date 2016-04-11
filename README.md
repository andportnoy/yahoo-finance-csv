# Yahoo Finance to CSV
A tiny Yahoo Finance API that lets you export ticker data as a Pandas DataFrame

# To-dos:
- [ ] add exception handling
- [ ] add tests
- [ ] add documentation
- [x] add pandas capabilities (option to return a pandas dataframe)
- [x] handle N/A values for data (using pandas)
- [ ] parse numeric values that can't be converted using `pd.to_numeric` (e.g. EBITDA with letters M, B for million and billion)
- [ ] add graphing capabilities (matplotlib or seaborn)

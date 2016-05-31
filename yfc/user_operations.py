from . import _data_operations as dataops
from ._exceptions import BadTickersFormatError


def current(tickers, write_to_csv=False, result_csv_path='data.csv'):

    """Retrieves realtime stock data from Yahoo Finance.


    :param tickers: list of tickers or path to ticker csv file
    :param write_to_csv: boolean, `current` writes the DataFrame to a csv file if set to `True` (`False` is default)
    :param result_csv_path: string, specifies path to csv file to write the data (overwrites the file)

    :returns: a pandas `DataFrame`
    """

    # create parameter string for the request
    api_dict = dataops.read_api_dict()
    param_list = dataops.get_param_list_from_api_dict(api_dict)
    param_string = dataops.get_param_string_from_list(param_list)

    # list of tickers or path to a csv file with tickers?
    try:
        if type(tickers) == str:
            ticker_list = sorted(dataops.get_ticker_list_from_file(tickers))
            ticker_string = dataops.get_ticker_string_from_list(ticker_list)

        elif type(tickers) == list:
            ticker_list = tickers
            ticker_string = dataops.get_ticker_string_from_list(ticker_list)
        else:
            raise BadTickersFormatError('Please provide either a csv file or a list of tickers.')
    except BadTickersFormatError as err:
        quit(err.message)
    else:
        # make request and create a pandas dataframe from the response
        answer_string = dataops.get_current_answer_string(ticker_string, param_string)
        answer_list = dataops.get_answer_list_from_string(answer_string)
        pandas_dataframe = dataops.current_pd_dataframe(api_dict, answer_list, param_list)

        if write_to_csv:
            pandas_dataframe.to_csv(result_csv_path)

        return pandas_dataframe


def historical(ticker, from_date=None, to_date=None, write_to_csv=False, result_csv_path=None):
    """Retrieves historical stock price data from Yahoo Finance.

    :param ticker: one ticker symbol
    :param from_date: lower bound for timeframe
    :param to_date: upper bound for timeframe

    `from_date` and `to_date` need to be formatted as 'YYYY-MM-DD'

    :returns: a pandas ``DataFrame``
    """

    answer_string = dataops.get_historical_answer_string(ticker, from_date, to_date)
    print('Got data for', ticker)
    answer_list = dataops.get_answer_list_from_string(answer_string)
    pandas_dataframe = dataops.historical_pd_dataframe(answer_list)

    if write_to_csv:
        pandas_dataframe.to_csv(result_csv_path)

    return pandas_dataframe


def mult_historical(tickers, write_to_csv=False, result_csv_path=None, how='outer'):
    """Returns a Pandas dataframe with historical data for multiple tickers side by side.

    :param tickers: list of tickers or path to ticker csv file
    :param write_to_csv: boolean, `mult_historical` writes the DataFrame to a csv file
            if set to `True` (`False` is default)
    :param result_csv_path: string, specifies path to csv file to write the data (overwrites existing file)
    :param how: specifies how the join should be made (outer join by default)
    :return: a pandas `DataFrame`
    """

    try:
        if type(tickers) == str:
            ticker_list = sorted(dataops.get_ticker_list_from_file(tickers))
        elif type(tickers) == list:
            ticker_list = tickers
        else:
            raise BadTickersFormatError('Please provide either a csv file or a list of tickers.')
    except BadTickersFormatError as err:
        quit(err.message)
    else:

        # TODO move all the reshaping business to dataops
        # get historical data for each ticker in ticker_list
        full_dfs = [historical(ticker) for ticker in ticker_list]

        # throw out the Nones
        not_nones = [(ticker, df) for ticker, df in zip(ticker_list, full_dfs) if df is not None]

        # use only the 'Close' column
        adj_close_only = [(ticker, df[['Adj Close']]) for ticker, df in not_nones]

        # replace 'Adj. Close' in all dataframes with their tickers
        renamed = [df.rename(columns={'Adj Close': ticker}) for ticker, df in adj_close_only]

        # inner-join all the dataframes by index ('Date')
        joined = renamed[0]
        for df in renamed[1:]:
            joined = joined.join(df, how=how)

        joined.columns = [name.upper() for name in list(joined.columns)]
        # TODO return a dataframe including all columns from historical data incorporated under a multiindex

        result = joined.sort_index()
        if write_to_csv:
            result.to_csv(result_csv_path)

        return result

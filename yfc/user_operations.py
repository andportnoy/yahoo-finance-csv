import _data_operations as dops
from ._decorators import *
from ._exceptions import *


@timeit
def current(tickers, write_to_csv=False, result_csv_path=None):
    """Retrieves realtime stock data from Yahoo Finance.

    Arguments:
        tickers --> list of tickers or path to ticker csv file
        write_to_csv --> boolean, current writes data to a csv file if set to True, returns a pandas dataframe
                         if set to False (default)
        result_csv_path --> string, specifies path to csv file to write the data (overwrites the file)

    Returns:
        a pandas dataframe or None (if write_to_csv is set to False)
    """

    # create parameter string for the request
    api_dict = dops.read_api_dict()
    param_list = dops.get_param_list_from_api_dict(api_dict)
    param_string = dops.get_param_string_from_list(param_list)

    # list of tickers or path to a csv file with tickers?
    try:
        if type(tickers) == str:
            ticker_list = sorted(dops.get_ticker_list_from_file(tickers))
            ticker_string = dops.get_ticker_string_from_list(ticker_list)

        elif type(tickers) == list:
            ticker_list = tickers
            ticker_string = dops.get_ticker_string_from_list(ticker_list)
        else:
            raise BadTickersFormat('Please provide either a csv file or a list of tickers.')
    except BadTickersFormat as err:
        quit(err.message)
    else:
        # make request and create a pandas dataframe from the response
        answer_string = dops.get_current_answer_string(ticker_string, param_string)
        answer_list = dops.get_answer_list_from_string(answer_string)
        pandas_dataframe = dops.current_pd_dataframe(api_dict, answer_list, param_list, ticker_list)

        if write_to_csv:
            pandas_dataframe.to_csv(result_csv_path)

        return pandas_dataframe


@timeit
def historical(ticker, from_date=None, to_date=None):
    """Retrieves historical stock price data from Yahoo Finance.

    Arguments:
        ticker --> one ticker symbol
        from_date --> lower bound for timeframe
        to_date --> upper bound for timeframe

        from_date and to_date can be of the following types:
            - string of form 'YYYY-MM-DD'
            - Python datetime
            - NumPy datetime64
            - Pandas Timestamp

    Returns:
        Pandas DataFrame
    """

    answer_string = dops.get_historical_answer_string(ticker, from_date, to_date)
    answer_list = dops.get_answer_list_from_string(answer_string)
    pandas_dataframe = dops.historical_pd_dataframe(answer_list)

    # TODO Finish this
    return pandas_dataframe


@timeit
def correlation_matrix(tickers):
    """Calculates a correlation matrix for the stocks in ticker_list."""

    try:
        if type(tickers) == str:
            ticker_list = sorted(dops.get_ticker_list_from_file(tickers))

        elif type(tickers) == list:
            ticker_list = tickers
        else:
            raise BadTickersFormat('Please provide either a csv file or a list of tickers.')
    except BadTickersFormat as err:
        quit(err.message)
    else:

        # iterate through tuples of tickers and corresponding dataframes
        full_dfs = zip(ticker_list, map(historical, ticker_list))

        # throw out the Nones
        not_nones = [(ticker, df) for ticker, df in full_dfs if df is not None]

        # use only the 'Close' column
        close_only = [(ticker, df[['Close']]) for ticker, df in not_nones]

        # replace 'Close' in all dataframes with their tickers
        renamed = [df.rename(columns={'Close': ticker}) for ticker, df in close_only]

        # inner-join all the dataframes by index ('Date')
        joined = reduce(lambda df1, df2: df1.join(df2, how='inner'), renamed)

        return joined.corr()

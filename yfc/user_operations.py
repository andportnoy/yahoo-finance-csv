import _data_operations as dops
from _decorators import *


@timeit
def current(tickers, write_to_csv=False, result_csv_path=None, api_dict_csv_path='yahoo_api_dict.csv'):
    """Wrapper function, performs data retrieval/storage using other functions.

    Arguments:
        tickers --> path to ticker csv file or list of tickers
        write_to_csv --> boolean, retrieve writes data to a csv file if set to True, returns a pandas dataframe
                         if set to False (default)
        result_csv_path --> string, specifies path to csv file to write the data (overwrites the file)
        api_dict_csv_path --> string, specifies path to csv file giving descriptions to Yahoo Finance parameters

    Returns:
        a pandas dataframe or None (if write_to_csv is set to False)
    """

    # create parameter string for the request
    api_dict = dops.get_api_dict_from_file(api_dict_csv_path)
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
            raise Exception('Please provide either a csv file or a list of tickers.')
    except Exception:
        quit(Exception.message)
    else:
        # make request and create a pandas dataframe from the response
        answer_string = dops.get_answer_string(ticker_string, param_string)
        answer_list = dops.get_answer_list_from_string(answer_string)
        pandas_dataframe = dops.make_pd_dataframe(api_dict, answer_list, param_list, ticker_list)

        if write_to_csv:
            pandas_dataframe.to_csv(result_csv_path)

        return pandas_dataframe

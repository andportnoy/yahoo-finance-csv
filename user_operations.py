import pandas as pd
import numpy as np
import data_operations as dops
from decorators import *


@timeit
def current(tickers, write_to_csv=False, result_csv_path=None, api_dict_csv_path='yahoo_api_dict.csv'):
    """Wrapper function, performs data retrieval/storage using other functions.

    Arguments:
        ticker_csv_path --> path to ticker csv file
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

    # create ticker string for the request

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

    # make request and transform it into a list
    answer_string = dops.get_answer_string(ticker_string, param_string)
    answer_list = dops.get_answer_list_from_string(answer_string)

    # lookup the parameter definitions and create a dictionary to be transformed into a pandas DataFrame
    dict_for_pandas = {api_dict[param_list[index]]: item for index, item in enumerate(zip(*answer_list))}
    pandas_dataframe = pd.DataFrame(dict_for_pandas)
    pandas_dataframe.index = ticker_list
    pandas_dataframe = pandas_dataframe.replace(to_replace='N/A', value=np.nan)

    # Drop columns that consist of NaN's only
    for item in pandas_dataframe:
        if pandas_dataframe[item].count() == 0:
            del pandas_dataframe[item]

    # Convert columns to numeric if possible, handle exception and print column name otherwise
    for colname in pandas_dataframe:
        try:
            pandas_dataframe[colname] = pd.to_numeric(pandas_dataframe[colname])
        except ValueError:
            print colname, 'could not be converted.'

    # TODO Convert columns to datetimes if possible
    # TODO Parse values with M, B for million/billion

    if write_to_csv:
        pandas_dataframe.to_csv(result_csv_path)

    return pandas_dataframe
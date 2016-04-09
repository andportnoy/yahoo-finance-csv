import requests
import csv


def get_api_dict_from_file(api_dict_csv_path, api_dict={}):
	"""Creates a dictionary of Yahoo Finance API parameters from a csv file.
	
	Arguments: 	string containing path to API dictionary file.
		File specs: csv with columns 'parameter, description'.
	Returns: 	a dictionary consisting of parameters and their descriptions.
	"""
	with open(api_dict_csv_path) as api:
		reader = csv.DictReader(api)
		for row in reader:
			param = row['parameter']
			desc = row['description']
			api_dict[param] = desc
	return api_dict


def get_ticker_list_from_file(tickers_csv_path, ticker_list=[]):
	"""Creates a list of tickers from a csv file listing tickers one per line.
	
	Arguments:	string containing path to tickers csv file.
		File specs: csv with column 'ticker'.
	Returns: 	a list of ticker strings.
	"""
	with open(tickers_csv_path) as tickers:
		reader = csv.DictReader(tickers)
		for row in reader:
			ticker_list.append(row['ticker'])
	return ticker_list


def get_ticker_string_from_list(ticker_list):
	"""Returns a string of tickers separated by commas joined from a list."""
	ticker_string = ','.join(ticker_list)
	return ticker_string


def get_param_list_from_api_dict(api_dict):
	"""Returns the keys of an API dictionary."""
	return api_dict.keys()


def get_param_string_from_list(param_list):
	"""Returns a string of parameters with no separators joined from a list."""
	return ''.join(param_list)


def get_answer_string(ticker_string, param_string):
	"""Queries Yahoo Finance API, returns a CSV string with the response.
	
	Arguments: 	comma-separated string of tickers, string of parameters.
	Returns: 	response string, CSV formatted.
	"""
	url = 'http://finance.yahoo.com/d/quotes.csv?s=' + ticker_string + '&f=' + param_string
	answer_string = requests.get(url).text
	return answer_string


def get_header_list(param_list, api_dict, header_list=[]):
	"""Creates a header for a CSV data file.
	
	Arguments: 	list of parameters, Yahoo API dictionary.
	Returns: 	list of parameter descriptions retrieved from the API dictionary.
	"""
	for param in param_list:
		header_list.append(api_dict[param])
	return header_list


def get_answer_list_from_string(answer_string):
	"""Creates a list from the response string.
	
	Arguments:	response string.
	Returns:	list generated from the string by comma-splitting.
	"""
	answer_list = answer_string.splitlines()
	for i in range(len(answer_list)):
		answer_list[i] = answer_list[i].split(',')
	return answer_list


def save_raw_answer_to_file(answer_path, answer_string):
	"""Saves the response string to a specified path.
	
	Arguments:	path to target, response string.
	Returns:	nothing.
	"""
	with open(answer_path, 'wb') as raw_data:
		raw_data.write(answer_string)
	print 'Raw response csv file saved to ' + answer_path


def construct_row(k, header_list, answer_list, row={}):
	"""Creates a row of data for a CSV file (to be used with csv.DictWriter).
	
	Arguments:	position of observation sublist on the response list, header list, 
			list formed from the response.
	Returns:	row of data in form of a dictionary.
	"""
	for i in range(len(header_list)):
		row[header_list[i]] = answer_list[k][i]
	return row


def save_formatted_csv(result_csv_path, header_list, ticker_list, answer_list):
	"""Writes the data from the response list to a CSV file using csv.DictWriter.
	
	Arguments:	path to target file, header list, list of tickers, response list.
	Returns:	nothing.
	"""
	with open(result_csv_path, 'wb') as data:
		fieldnames = ['ticker'] + header_list
		writer = csv.DictWriter(data, fieldnames, quoting=csv.QUOTE_NONE, escapechar=' ')
		writer.writeheader()
		for k in range(len(ticker_list)):
			row = construct_row(k, header_list, answer_list)
			row['ticker'] = ticker_list[k]
			writer.writerow(row)


def get_data(tickers_csv_path, result_csv_path):
	"""Wrapper function, performs data retrieval/storage using other functions.
	
	Arguments:	path to CSV file with tickers, path to write target for the data.
	Returns:	nothing.
	"""
	api_dict_csv_path = 'yahoo_api_dict.csv'

	# create parameter string for the request
	api_dict = get_api_dict_from_file(api_dict_csv_path)
	param_list = get_param_list_from_api_dict(api_dict)
	param_string = get_param_string_from_list(param_list)

	# create ticker string for the request
	ticker_list = get_ticker_list_from_file(tickers_csv_path)
	ticker_string = get_ticker_string_from_list(ticker_list)

	# make request and transform it into a list
	answer_string = get_answer_string(ticker_string, param_string)
	answer_list = get_answer_list_from_string(answer_string)

	# create the csv file with resulting data
	header_list = get_header_list(param_list, api_dict)
	save_formatted_csv(result_csv_path, header_list, ticker_list, answer_list)

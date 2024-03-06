import http.client
import os
import re
import urllib

import arxiv
from dotenv import load_dotenv


# Load environment variables from .env file
# Construct the path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# Load the .env file
load_dotenv(dotenv_path)

# Access environment variables
API_KEY = os.getenv('APP_TOKEN')
USER_KEY = os.getenv('USER_TOKEN')
HOME_PATH = os.getenv('HOME_PATH')

# Functions


def find_last_hyperlink_end(s: str, limit: int = 1024) -> int:
    """
    Find the end index of the last hyperlink within the first `limit` characters of a string.

    Parameters:
    - s (str): The input string.
    - limit (int): The maximum number of characters to search within, default is 1024.

    Returns:
    - int: The end index of the last hyperlink found within the limit, or -1 if none found.
    """
    # Adjust the limit if it's beyond the string's length
    limit = min(limit, len(s))

    # Regular expression to find hyperlinks
    pattern = r'https?://[^\s]+'

    # Find all hyperlinks within the limit
    matches = [match for match in re.finditer(pattern, s[:limit])]

    if matches:
        # Return the end index of the last match
        return matches[-1].end()
    else:
        return -1

def split_text_by_hyperlinks(s: str) -> list:
    """
    Split the text into parts based on hyperlinks, where each part ends with a hyperlink
    and is up to 1024 characters long.

    Parameters:
    - s (str): The input string.

    Returns:
    - list: A list of string parts, each ending with a hyperlink and up to 1024 characters long.
    """
    parts = []
    while len(s) > 1024:
        end_index = find_last_hyperlink_end(s, 1024)
        if end_index == -1:  # No hyperlink found within 1024 characters
            # Split at 1024 if no hyperlink is found
            parts.append(s[:1024])
            s = s[1024:]
        else:
            # Include the hyperlink in the current part
            parts.append(s[:end_index])
            # Start the next part after the hyperlink
            s = s[end_index:]
    parts.append(s)  # Add the remaining part of the string
    return parts

def remove_known_entries(data: dict, existing_titles: list):
    """
    Remove entries from the data dictionary whose titles exist in the existing_titles list.

    Parameters:
    - data (dict): A dictionary of data entries.
    - existing_titles (list): A list of titles to be removed from the data.
    """
    for key in list(data.keys()):
        if data[key]['title'] in existing_titles:
            del data[key]


def extract_information(data, key="title"):
    """
    Extract information based on a specified key from each entry in the data dictionary.

    Parameters:
    - data (dict): A dictionary of data entries.
    - key (str): The key to extract information from each entry. Defaults to "title".

    Returns:
    - list: A list of extracted information from each data entry.
    """
    titles = []
    for i in list(data.keys()):
        output = data[i][key]
        titles.append(output)
    return titles


def turn_into_tuples(data: dict) -> list:
    """
    Convert the data dictionary into a list of tuples containing specified information.

    Parameters:
    - data (dict): A dictionary of data entries.

    Returns:
    - list: A list of tuples, each containing the 'title' and 'entry_id' of an entry.
    """
    return [(v['title'], v['entry_id']) for v in data.values()]


def read_list_from_file(file_path):
    """
    Read a list of strings from a specified file.

    Parameters:
    - file_path (str): The path to the file to be read.

    Returns:
    - list: A list of strings read from the file.
    """
    with open(file_path, 'r') as file:
        content = file.read()
    return content.split('\n')[:-1]


def append_titles_to_file(new_titles, file_path):
    """
    Append new titles to an existing file.

    Parameters:
    - new_titles (list): A list of new titles to append.
    - file_path (str): The path to the file where titles will be appended.
    """
    with open(file_path, 'a') as file:
        # Ensure there's a newline at the start to separate from existing content
        file.write('\n'.join(new_titles) + '\n')


def search_arvix(field="cs.cv", title_keyword="low field MRI"):
    """
    Search the arXiv for papers matching a specific field and title keyword.

    Parameters:
    - field (str): The field to search within. Defaults to "cs.cv".
    - title_keyword (str): The keyword to search in titles. Defaults to "low field MRI".

    Returns:
    - tuple: Two dictionaries containing search results sorted by SubmittedDate and Relevance.
    """
    client = arxiv.Client()

    # initialise searches for both SubmittedDate and Relevance
    sort_criteria = [arxiv.SortCriterion.SubmittedDate, arxiv.SortCriterion.Relevance]
    results = {}

    for criterion in sort_criteria:
        search = arxiv.Search(
            query=f"{field} AND {title_keyword}",
            max_results=50 if criterion == arxiv.SortCriterion.Relevance else 30,
            sort_by=criterion
        )
        results[criterion] = {idx: {"title": r.title, "entry_id": r.entry_id} for idx, r in enumerate(client.results(search))}

    submitted_date_titles = results[arxiv.SortCriterion.SubmittedDate]
    relevance_titles = results[arxiv.SortCriterion.Relevance]

    return relevance_titles, submitted_date_titles


def join_tuples(tuples_list):
    """
    Join a list of tuples into a single string, with each tuple converted to a string and separated by a newline.

    Parameters:
    - tuples_list (list): A list of tuples to be joined.

    Returns:
    - str: A single string representation of the list of tuples.
    """
    # Convert each tuple to a string by joining each element with a space
    tuples_str = [" ".join(map(str, t)) for t in tuples_list]
    # Join the list of strings with "\n" to get a single string
    result = "\n".join(tuples_str)
    return result


def push_to_device(api_key, user_key, message, header):
    """
    Push a message to a device using the Pushover API.

    Parameters:
    - api_key (str): The API key for authentication.
    - user_key (str): The user key for the target device.
    - message (str): The message to be sent.
    - header (str): A descriptor for the message, e.g., "Relevance" or "SubmittedDate".
    """
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
        "token": api_key,
        "user": user_key,
        "title": f"Daily Paper Dump | {header}",
        "message": message,
        "sound": "vibrate",
        }), {"Content-type": "application/x-www-form-urlencoded"})
    conn.getresponse()

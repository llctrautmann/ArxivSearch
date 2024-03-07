# ArXiv Paper Parser

NOTE: THIS PROJECT IS STILL IN TESTING PHASE

The ArXiv Paper Parser is a Python-based tool designed to automate the process of fetching, filtering, and notifying users about new academic papers published on the arXiv platform, based on predefined search criteria. It focuses on providing updates in specific research fields and keywords, managing a list of known papers to avoid duplicates, and pushing notifications to a user's device.

## Features

- **Customizable Searches**: Users can specify fields and keywords to tailor the search to their interests.
- **Duplicate Avoidance**: The tool tracks previously fetched papers to prevent duplicate notifications.
- **Notification System**: Utilizes the Pushover API to send updates directly to the user's device.

## Key Components

- **Search Functionality**: Utilizes the`arxiv` Python package to query the arXiv API.
- **Data Handling**: Processes and stores data in text files, handling both new and existing entries.
- **Notification Mechanism**: Sends alerts through Pushover for new relevant papers.

## Setup

1. **Dependencies**: Install required packages from `requirements.txt` and `requirements-dev.txt`.
2. 
    ```bash
    pip install -r requirements.txt
    ```

3. **Environment Variables**: Set up `.env` with Pushover API and User keys.
    ```plaintext
    APP_TOKEN=<your-app-token>
    USER_TOKEN=<your-user-token>
    ```
The .env file need to be setup by the user following the above example.

4. **Configuration**: Adjust search parameters in `src/main.py` as needed.
    ```python:src/main.py
    field="cat:cs.cv OR cat:eess.iv",
    title_keyword="ti:low field MRI OR all:low field MRI OR ti:low field magnetic resonance imaging"
    ```
Information on categories can be found [here](https://info.arxiv.org/help/api/user-manual.html#query_details) and general taxonomy [here](https://arxiv.org/category_taxonomy).

## Usage

Run the main script to start the process:
```bash
python src/main.py
```

Ideally setup with `crontab` for daily execution. Info for MacOS [here](https://apple.stackexchange.com/questions/402132/cronjobs-do-not-run)

The script performs the following steps:
1. Reads the current status of papers from `Relevance.txt` and `SubmittedDate.txt`.
2. Searches for new papers based on the specified criteria.
3. Filters out known entries to avoid duplicates.
4. Appends new titles to the respective files.
5. Sends notifications about new papers (title and Arxiv link).

## Customization

- **Search Criteria**: Modify the `field` and `title_keyword` parameters in `src/main.py` to change the search focus.
- **Notification Details**: Adjust the message format and content in `src/utils.py` within the `push_to_device` function.

## Files and Directories

- `src/`: Contains the main script and utility functions.
- `notebooks/`: Jupyter notebooks for testing and development.
- `.env`: Environment file for storing API keys.
- `Relevance.txt` and `SubmittedDate.txt`: Text files for tracking known papers.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests with your proposed changes.

## License

This project is open-source and available under the GNU open source licence

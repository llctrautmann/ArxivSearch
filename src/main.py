from utils import *


def main(field, title_keyword):
    """
    Main function to process new papers from arXiv based on predefined criteria.

    This function performs several steps:
    1. Reads the current status of papers (titles) from files for relevance and submitted date.
    2. Calls the arXiv API to search for new papers based on predefined search criteria.
    3. Removes known entries from the new papers fetched to avoid duplicates.
    4. Extracts titles from the new papers and appends them to the respective files.
    5. Pushes notifications about the new papers to a device using the Pushover API.
    """
    current_status_relevance = read_list_from_file("Relevance.txt") # list of strings
    current_status_submitted_date = read_list_from_file("SubmittedDate.txt") # list of strings

    current_status = [current_status_relevance, current_status_submitted_date]
    headers = ["Relevance", "SubmittedDate"]

    # Call API for new paper
    queries = search_arvix(field, title_keyword)

    for idx, query in enumerate(queries):
        remove_known_entries(query, current_status[idx])
        new_relevance_titles = extract_information(query)
        # append_titles_to_file(new_relevance_titles, f"{headers[idx]}.txt")

        payload = join_tuples(turn_into_tuples(query))

        if len(new_relevance_titles) > 0:
            parts = [part.lstrip() for part in split_text_by_hyperlinks(payload)][::-1]

            for idy, part in enumerate(parts):
                if len(parts) > 1:
                    push_to_device(API_KEY, USER_KEY, part, f"{headers[idx]} | Part {-idy + len(parts)}")
                else:
                    push_to_device(API_KEY, USER_KEY, part, f"{headers[idx]}")
        else:
            push_to_device(API_KEY, USER_KEY, "No new papers", f"{headers[idx]}")

if __name__ == "__main__":
    main(
        field="cs.cv OR cat:eess.iv",
        title_keyword="low field MRI OR all:low field MRI OR ti:low field magnetic resonance imaging"
        )

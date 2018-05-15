"""Module that provides pagination and supporting functionality."""


def pagination(entries, num_entries=15, ):
    """
    :param entries: List of all of the entries that need to be paginated (if necessary)
    :param num_entries: number of entries that should be provided per page
    :return: list of dictionaries that should be passed to the publisher with the appropriate prev and next values
    set for the URLs
    """

    # Split the entries into chunks of num_entries size
    chunks = [entries[x:x+num_entries] for x in range(0, len(entries), num_entries)]

    # Populate the rest of the data set with values for finding the next pages
    return_value = []
    for page_number, page in enumerate(chunks, start=1):
        page_data = {'entries': page,
                     'page_number': page_number}

        if page_number != 1:
            page_data['prev_page_number'] = page_number - 1

        if page_number != len(chunks):
            page_data['next_page_number'] = page_number + 1

        return_value.append(page_data)

    return return_value

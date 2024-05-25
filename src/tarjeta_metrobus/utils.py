from bs4 import Tag
from slugify import slugify


def bs_table_to_dict(table: Tag):
    '''
    Convert a bs4 table to a dict

    Args:
        table (Tag): bs4 table
    Returns:
        dict
    '''

    data = {}
    table_data = [[cell.text for cell in row("td")] for row in table.find_all("tr")]

    table_data = [*table_data[0], *table_data[1]]

    for i in range(0, len(table_data), 2):
        data[slugify(table_data[i], separator='_')] = (table_data[i + 1]).strip()

    return data


def table_to_data(soup, text_in_table):
    table_tile = soup.find(string=text_in_table)
    if table_tile is None:
        return None

    table = table_tile.parent.parent.parent.parent
    table_data = [[cell.text.strip() for cell in row("td")] for row in table.find_all("tr")]

    table_data = table_data[1::]
    keys = ['month', 'amount', 'count']
    merged_columns = zip(table_data[0][1:], table_data[1][1:],  table_data[2][1:])

    return [dict(zip(keys, values)) for values in merged_columns]

from bs4 import BeautifulSoup


def parse_html_table(html: str):

    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")

    if not table:
        return []

    rows = table.find_all("tr")

    if not rows:
        return []

    parsed_rows = []

    for row in rows:

        cells = [
            cell.get_text(" ", strip=True)
            for cell in row.find_all(["th", "td"])
        ]

        if cells:
            parsed_rows.append(cells)

    if not parsed_rows:
        return []

    # Vertical vendor metadata table
    if (
        len(parsed_rows[0]) == 2
        and parsed_rows[0][0] in {
            "Vendor",
            "Field",
            "Question",
            "Key",
        }
    ):

        data = [
            {
                parsed_rows[0][0]: parsed_rows[0][1]
            }
        ]

        for row in parsed_rows[1:]:

            if len(row) >= 2:

                data.append(
                    {
                        row[0]: row[1]
                    }
                )

        return data

    # Normal horizontal table
    headers = parsed_rows[0]

    data = []

    for row in parsed_rows[1:]:

        row_data = dict(
            zip(headers, row)
        )

        data.append(row_data)

    return data
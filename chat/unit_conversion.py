import re
from pint import UnitRegistry

ureg = UnitRegistry()

def convert_with_pint(query):
    query = query.lower().strip()
    print(f"User query: {query}")

    pattern_how_many = re.compile(
        r"how\s+many\s+([\w\s]+?)\s+in\s+(\d*\.?\d+)\s*(\w+)", re.IGNORECASE
    )
    match_how_many = pattern_how_many.search(query)

    if match_how_many:
        to_unit = match_how_many.group(1).strip()
        value = float(match_how_many.group(2))
        from_unit = match_how_many.group(3).strip()

        try:
            quantity = value * ureg(from_unit)
            converted = quantity.to(to_unit)
            return f"{value} {from_unit} is equal to {converted.magnitude:.4f} {to_unit}."
        except Exception as e:
            return f"Conversion error: {e}"

    pattern_convert = re.compile(
        r"convert\s+([-+]?\d*\.?\d+)\s+([\w\s]+?)\s+to\s+([\w\s]+?)", re.IGNORECASE
    )
    match_convert = pattern_convert.search(query)

    if match_convert:
        value = float(match_convert.group(1))
        from_unit = match_convert.group(2).strip()
        to_unit = match_convert.group(3).strip()

        try:
            quantity = value * ureg(from_unit)
            converted = quantity.to(to_unit)
            return f"{value} {from_unit} is equal to {converted.magnitude:.4f} {to_unit}."
        except Exception as e:
            return f"Conversion error: {e}"

    # Handle common time-related questions (improved)
    time_queries = {
        "days in a week": "There are 7 days in a week.",
        "days in a month": "On average, there are about 30.44 days in a month.",
        "days in a year": "There are 365 days in a year, or 366 in a leap year.",
        "hours in a day": "There are 24 hours in a day."
    }
    for phrase, response in time_queries.items():
        if phrase in query:  # Check for the *phrase* within the query
            return response


    return "No conversion matched. Please try a different query."

if __name__ == "__main__":
    while True:
        query = input("Enter a conversion query (or type 'exit' to quit): ")
        if query.lower() == "exit":
            break
        print(convert_with_pint(query))
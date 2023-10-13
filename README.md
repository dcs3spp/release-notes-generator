# Release Notes ChangeLog Generator

This is a Python script that outputs markdown changelog from Gateway and Dashboard from a CSV file named release.csv.
The CSV file is expected to be produced from a confluence table copied into a spreadsheet and exported as CSV.

The CSV parser parses the following column headings:

- Component/S
- Release Notes*
- Change

Ensure the following:
- Component/S column is completed and contains no blank values. The script will report rows that contain 
blank values and offer to continue generating the markdown. The parser recognises the following values in the Component/S column (Tyk Portal (old), Tyk Portal, Tyk Dashboard, Documentation, Tyk Gateway, Internal, None, Tyk Plugin, Tyk Pump)
- Add a Change column that contains one of the enumerated values (Add, Deleted, Deprecated, Fix, Internal, None or Update).
The script will report rows that contain blank values and offer to continue generating the markdown.

The Component/S column can contain multiple values, separated by a comma. For example: Tyke Dashboard, Tyk Gateway.


## Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/)
- CSV file in root of repository named release-notes.csv

## Python Dependencies

The Python dependencies are listed in the *pyproject.toml* file in the root of the repository

## Running The Script

Use poetry to install the Python dependencies and then run the script using the provide make rule.

```console
poetry install
make run-poetry
```

The script will output the changelog to console for Dashboard and Gateway.

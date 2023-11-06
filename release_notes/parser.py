import csv
import logging

from enum import StrEnum
from typing import Any, Optional
from pydantic import BaseModel
from release_notes.models import (
    ChangeLog,
    ProductChangeLog,
    ReleaseNote,
    ChangeEnum,
    ProductEnum,
)

logger = logging.getLogger(__name__)


class _Column(StrEnum):
    PRODUCT = "Component/S"
    RELEASE_NOTE = "Release Notes*"
    CHANGE_TYPE = "Change"


class _ParsedRow(BaseModel):
    parseErrors: list[str]
    products: list[ProductEnum]
    change: Optional[ChangeEnum]
    releaseNote: Optional[str]


def _validate_change(change: str, row: int) -> ChangeEnum:
    """Create a ChangeEnum from a string value

    @param change (str) - The change string value
    @param row (int) - The row the change value is located in

    @return ChangeEnum for corresponding string v`lue
    @raise ValueError if unexpected change value encountered
    """

    try:
        return ChangeEnum(change)
    except ValueError:
        message = f"Invalid changelog type {change} : line: {row}"

        logger.error(message)

        raise ValueError(message)


def _validate_products(productColumn: str, row: int) -> list[ProductEnum]:
    """Inspect the product column and split by ,

    @param productColumn (str) - string of products separated by ,
    @param row (int) - The row number in csv the column relates to

    @return list[ProductEnum]
    @raise ValueError if unexpected product type encountered
    """

    products = list(productColumn.strip().split(","))

    _errors = []
    _validProducts = []

    for rowIndex, product in enumerate(products):
        try:
            product = product.strip()
            _validProduct = ProductEnum(product)
            _validProducts.append(_validProduct)
        except ValueError:
            _errors.append({"product": product, "row": row})

    if len(_errors) > 0:
        message = f"Invalid products encountered [{str(_errors)}] : line: {rowIndex}"
        raise ValueError(message)

    return _validProducts


def _validate(data: dict[str | Any, str | Any], row: int) -> _ParsedRow:
    """Parse a row in the release note csv file, returning data and errors

    @param data (dict[str|Any, str|Any]): A line of data from the CSV file
    @param row (int): The row number in the CSV file

    @returns A _ParsedRow instance containing parsed data and errors
    """

    _parseErrors = []
    productColumn = data.get(str(_Column.PRODUCT))
    releaseNotesColumn = data.get(str(_Column.RELEASE_NOTE))
    changeTypeColumn = data.get(str(_Column.CHANGE_TYPE))

    if not productColumn:
        message = f"Empty product value in column {_Column.PRODUCT.name} @ row {row}"
        _parseErrors.append(message)

    if not changeTypeColumn:
        message = f"Empty changelog type value in column {_Column.CHANGE_TYPE.name} @ row : {row}"
        _parseErrors.append(message)

    if not releaseNotesColumn:
        message = f"Empty release notes value in column {_Column.RELEASE_NOTE.name} @ row : {row}"
        _parseErrors.append(message)

    products = []
    change = None

    try:
        change = _validate_change(changeTypeColumn, row) if changeTypeColumn else None
        products = _validate_products(productColumn, row) if productColumn else []
    except ValueError as ve:
        _parseErrors.append(str(ve))

    return _ParsedRow(
        parseErrors=_parseErrors,
        products=products,
        change=change,
        releaseNote=releaseNotesColumn,
    )


def _createChangeLogEntry(
    product: ProductEnum,
    change: ChangeEnum,
    desciption: str,
    productChangeLog: dict[str, ProductChangeLog],
    row: int,
) -> None:
    """Create a change log entry for a given product

    @param product (ProductEnum): Product that the changelog entry relates to
    @param change (ChangeEnum): The changelog type
    @param description (str): The description for the changelog
    @param productChangeLog (ProductChangeLog): Dictionary containing changelog
        entries indexed by product
    @param row (int): The row the changelog relates to

    @raise ValueError If encounter an unexpected changelog type
    """

    if product not in productChangeLog:
        productChangeLog[product] = ProductChangeLog(
            changelog=ChangeLog(), product=product
        )

    match change:
        case "Add":
            productChangeLog[product].changelog.added.append(desciption)
        case "deleted":
            productChangeLog[product].changelog.deleted.append(desciption)
        case "deprecated":
            productChangeLog[product].changelog.deprecated.append(desciption)
        case "Fix":
            productChangeLog[product].changelog.fixed.append(desciption)
        case "Update":
            productChangeLog[product].changelog.updated.append(desciption)
        case _:
            message = f"Unknown change type: {change.name} at row {row}"
            logger.error(message)

            ValueError(message)


def parse(csvAbsolutePath: str, summary: str, semanticVersion: str) -> ReleaseNote:
    """Parse a CSV file and return a ReleaseNote object

    The release note contains changelog, summary and semantic version

    @param cvsAbsolutePath (str): The absolute path to the csv file
    @param sumary (str): The release note summary
    @param semanticVersion (str): Semantic version for release

    @returns A ReleaseNote instance containing the change logs for Tyk products,
    the release summary and semantic version. Additionally parsing errors
    encountered are encapsulated.
    """

    _ignoreChangeTypes: set[str] = {"Internal"}
    _ignoreProductValues: set[str] = {"Documentation", "None", "Tyk Pump"}
    _lines = []
    _productChangeLog: dict[str, ProductChangeLog] = {}
    _rowParseErrors: dict[int, list[str]] = {}

    try:
        with open(csvAbsolutePath) as csvfile:
            _lines = list(csv.DictReader(csvfile))

            row = 1

            for data in _lines:
                parsedRow = _validate(data, row)

                if parsedRow.parseErrors:
                    _rowParseErrors[row] = parsedRow.parseErrors
                    continue

                for product in parsedRow.products:
                    if product in _ignoreProductValues:
                        continue

                    if parsedRow.change in _ignoreChangeTypes:
                        continue

                    if (
                        parsedRow.change is not None
                        and parsedRow.releaseNote is not None
                    ):
                        _createChangeLogEntry(
                            product,
                            parsedRow.change,
                            parsedRow.releaseNote,
                            _productChangeLog,
                            row,
                        )

                row += 1
    except Exception as ex:
        logger.error(f"Failed to read file {csvAbsolutePath} with error {str(ex)}")
        raise ex

    print(f"Parsed {len(_lines)} lines in file {csvAbsolutePath}")

    return ReleaseNote(
        changelogs=_productChangeLog,
        rowParseErrors=_rowParseErrors,
        semanticVersion=semanticVersion,
        summary=summary,
    )

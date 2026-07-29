"""The three transaction exports, which differ only in output format."""

from typing import ClassVar

from aioplatega.types import ExportUrlResponse, TransactionExportRequest, TransactionExportResponse

from .base import PlategaMethod


class ExportTransactionsCsv(TransactionExportRequest, PlategaMethod[ExportUrlResponse]):
    """POST ``/transaction/export/csv`` — returns a link to the file."""

    __api_method__: ClassVar[str] = "/transaction/export/csv"
    __http_method__: ClassVar[str] = "POST"
    __returning__: ClassVar[type] = ExportUrlResponse


class ExportTransactionsExcel(TransactionExportRequest, PlategaMethod[ExportUrlResponse]):
    """POST ``/transaction/export/excel`` — returns a link to the file."""

    __api_method__: ClassVar[str] = "/transaction/export/excel"
    __http_method__: ClassVar[str] = "POST"
    __returning__: ClassVar[type] = ExportUrlResponse


class ExportTransactionsJson(TransactionExportRequest, PlategaMethod[TransactionExportResponse]):
    """POST ``/transaction/export/json``.

    The odd one out: it returns the rows inline rather than a download link.
    """

    __api_method__: ClassVar[str] = "/transaction/export/json"
    __http_method__: ClassVar[str] = "POST"
    __returning__: ClassVar[type] = TransactionExportResponse

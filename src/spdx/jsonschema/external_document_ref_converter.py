# SPDX-FileCopyrightText: 2022 spdx contributors
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any, Type

from spdx.jsonschema.checksum_converter import ChecksumConverter
from spdx.jsonschema.converter import TypedConverter
from spdx.jsonschema.external_document_ref_properties import ExternalDocumentRefProperty
from spdx.jsonschema.json_property import JsonProperty
from spdx.model.document import Document
from spdx.model.external_document_ref import ExternalDocumentRef


class ExternalDocumentRefConverter(TypedConverter[ExternalDocumentRef]):
    checksum_converter: ChecksumConverter

    def __init__(self):
        self.checksum_converter = ChecksumConverter()

    def _get_property_value(
        self,
        external_document_ref: ExternalDocumentRef,
        external_document_ref_property: ExternalDocumentRefProperty,
        _document: Document = None,
    ) -> Any:
        if external_document_ref_property == ExternalDocumentRefProperty.EXTERNAL_DOCUMENT_ID:
            return external_document_ref.document_ref_id
        elif external_document_ref_property == ExternalDocumentRefProperty.SPDX_DOCUMENT:
            return external_document_ref.document_uri
        elif external_document_ref_property == ExternalDocumentRefProperty.CHECKSUM:
            return self.checksum_converter.convert(external_document_ref.checksum)

    def get_json_type(self) -> Type[JsonProperty]:
        return ExternalDocumentRefProperty

    def get_data_model_type(self) -> Type[ExternalDocumentRef]:
        return ExternalDocumentRef

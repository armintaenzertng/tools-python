# SPDX-FileCopyrightText: 2022 spdx contributors
#
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from unittest import TestCase

import pytest

from spdx.constants import DOCUMENT_SPDX_ID
from spdx.model.actor import Actor, ActorType
from spdx.model.checksum import Checksum, ChecksumAlgorithm
from spdx.model.external_document_ref import ExternalDocumentRef
from spdx.model.version import Version
from spdx.parser.error import SPDXParsingError
from spdx.parser.jsonlikedict.creation_info_parser import CreationInfoParser


def test_parse_creation_info():
    creation_info_parser = CreationInfoParser()
    doc_dict = {
        "spdxVersion": "2.3",
        "SPDXID": DOCUMENT_SPDX_ID,
        "name": "Example Document",
        "dataLicense": "CC0-1.0",
        "documentNamespace": "namespace",
        "externalDocumentRefs": [
            {
                "externalDocumentId": "DocumentRef-spdx-tool-1.2",
                "checksum": {"algorithm": "SHA1", "checksumValue": "d6a770ba38583ed4bb4525bd96e50461655d2759"},
                "spdxDocument": "http://spdx.org/spdxdocs/spdx-tools-v1.2-3F2504E0-4F89-41D3-9A0C-0305E82C3301",
            }
        ],
        "creationInfo": {
            "created": "2010-01-29T18:30:22Z",
            "creators": ["Tool: LicenseFind-1.0", "Organization: ExampleCodeInspect ()", "Person: Jane Doe ()"],
            "licenseListVersion": "3.7",
            "comment": "Some comment.",
        },
    }
    creation_info = creation_info_parser.parse_creation_info(doc_dict)

    assert creation_info.spdx_version == "2.3"
    assert creation_info.spdx_id == DOCUMENT_SPDX_ID
    assert creation_info.name == "Example Document"
    assert creation_info.document_namespace == "namespace"
    assert creation_info.created == datetime(2010, 1, 29, 18, 30, 22)
    TestCase().assertCountEqual(
        creation_info.creators,
        [
            Actor(ActorType.TOOL, "LicenseFind-1.0"),
            Actor(ActorType.ORGANIZATION, "ExampleCodeInspect"),
            Actor(ActorType.PERSON, "Jane Doe"),
        ],
    )
    assert creation_info.license_list_version == Version(3, 7)
    assert creation_info.external_document_refs == [
        ExternalDocumentRef(
            document_ref_id="DocumentRef-spdx-tool-1.2",
            checksum=Checksum(algorithm=ChecksumAlgorithm.SHA1, value="d6a770ba38583ed4bb4525bd96e50461655d2759"),
            document_uri="http://spdx.org/spdxdocs/spdx-tools-v1.2-3F2504E0-4F89-41D3-9A0C-0305E82C3301",
        )
    ]


@pytest.mark.parametrize(
    "incomplete_dict,expected_message",
    [
        (
            {"spdxVersion": "2.3", "SPDXID": DOCUMENT_SPDX_ID, "name": "Example Document"},
            ["Error while parsing document Example Document: ['CreationInfo does not exist.']"],
        ),
        (
            {"creationInfo": {"created": "2019-02-01T11:30:40Z"}},
            [
                "Error while constructing CreationInfo: ['SetterError CreationInfo: type of "
                'argument "spdx_version" must be str; got NoneType instead: None\', '
                '\'SetterError CreationInfo: type of argument "spdx_id" must be str; got '
                "NoneType instead: None', 'SetterError CreationInfo: type of argument "
                "\"name\" must be str; got NoneType instead: None', 'SetterError "
                'CreationInfo: type of argument "document_namespace" must be str; got '
                "NoneType instead: None', 'SetterError CreationInfo: type of argument "
                "\"creators\" must be a list; got NoneType instead: None', 'SetterError "
                'CreationInfo: type of argument "data_license" must be str; got NoneType '
                "instead: None']"
            ],
        ),
    ],
)
def test_parse_incomplete_document_info(incomplete_dict, expected_message):
    creation_info_parser = CreationInfoParser()

    with pytest.raises(SPDXParsingError) as err:
        creation_info_parser.parse_creation_info(incomplete_dict)

    TestCase().assertCountEqual(err.value.get_messages(), expected_message)


def test_parse_invalid_creation_info():
    creation_info_parser = CreationInfoParser()
    doc_dict = {
        "spdxVersion": "2.3",
        "SPDXID": DOCUMENT_SPDX_ID,
        "name": "Example Document",
        "creationInfo": {
            "created": "2010-01-29T18:30:22Z",
            "creators": ["Tool: LicenseFind-1.0", "Organization: ExampleCodeInspect ()", "Person: Jane Doe ()"],
        },
        "dataLicense": None,
    }

    with pytest.raises(SPDXParsingError) as err:
        creation_info_parser.parse_creation_info(doc_dict)

    TestCase().assertCountEqual(
        err.value.get_messages(),
        [
            "Error while constructing CreationInfo: ['SetterError CreationInfo: type of "
            'argument "document_namespace" must be str; got NoneType instead: None\', '
            '\'SetterError CreationInfo: type of argument "data_license" must be str; got '
            "NoneType instead: None']"
        ],
    )

# SPDX-FileCopyrightText: 2022 spdx contributors
#
# SPDX-License-Identifier: Apache-2.0
import json
import os

import pytest

from spdx.writer.json.json_writer import write_document
from tests.spdx.fixtures import document_fixture


@pytest.fixture
def temporary_file_path() -> str:
    temporary_file_path = "temp_test_json_writer_output.json"
    yield temporary_file_path
    os.remove(temporary_file_path)


def test_write_json(temporary_file_path: str):
    document = document_fixture()
    write_document(document, temporary_file_path, validate=True)

    with open(temporary_file_path) as written_file:
        written_json = json.load(written_file)

    with open(os.path.join(os.path.dirname(__file__), "expected_results", "expected.json")) as expected_file:
        expected_json = json.load(expected_file)

    assert written_json == expected_json


def test_document_is_validated():
    document = document_fixture()
    document.creation_info.spdx_id = "InvalidId"

    with pytest.raises(ValueError) as error:
        write_document(document, "dummy_path")
    assert "Document is not valid" in error.value.args[0]


def test_document_validation_can_be_overridden(temporary_file_path: str):
    document = document_fixture()
    document.creation_info.spdx_id = "InvalidId"

    write_document(document, temporary_file_path, validate=False)

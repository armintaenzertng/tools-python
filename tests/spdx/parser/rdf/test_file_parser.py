# SPDX-FileCopyrightText: 2023 spdx contributors
#
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import TestCase

from license_expression import get_spdx_licensing
from rdflib import RDF, Graph, URIRef

from spdx.model.checksum import Checksum, ChecksumAlgorithm
from spdx.model.file import FileType
from spdx.model.spdx_no_assertion import SpdxNoAssertion
from spdx.parser.rdf.file_parser import parse_file
from spdx.rdfschema.namespace import SPDX_NAMESPACE


def test_parse_file():
    graph = Graph().parse(os.path.join(os.path.dirname(__file__), "data/file_to_test_rdf_parser.rdf.xml"))
    file_node = graph.value(predicate=RDF.type, object=SPDX_NAMESPACE.File)
    doc_namespace = "https://some.namespace"
    assert isinstance(file_node, URIRef)

    file = parse_file(file_node, graph, doc_namespace)

    assert file.name == "./fileName.py"
    assert file.spdx_id == "SPDXRef-File"
    assert file.checksums == [Checksum(ChecksumAlgorithm.SHA1, "71c4025dd9897b364f3ebbb42c484ff43d00791c")]
    assert file.file_types == [FileType.TEXT]
    assert file.comment == "fileComment"
    assert file.copyright_text == "copyrightText"
    assert file.contributors == ["fileContributor"]
    assert file.license_concluded == get_spdx_licensing().parse("MIT AND GPL-2.0")
    TestCase().assertCountEqual(
        file.license_info_in_file,
        [get_spdx_licensing().parse("MIT"), get_spdx_licensing().parse("GPL-2.0"), SpdxNoAssertion()],
    )
    assert file.license_comment == "licenseComment"
    assert file.notice == "fileNotice"
    assert file.attribution_texts == ["fileAttributionText"]

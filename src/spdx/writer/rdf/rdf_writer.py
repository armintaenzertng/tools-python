# SPDX-FileCopyrightText: 2023 spdx contributors
#
# SPDX-License-Identifier: Apache-2.0
from typing import Dict, List

from rdflib import DOAP, Graph
from rdflib.compare import to_isomorphic

from spdx.model.document import Document
from spdx.rdfschema.namespace import POINTER_NAMESPACE, SPDX_NAMESPACE
from spdx.validation.document_validator import validate_full_spdx_document
from spdx.validation.validation_message import ValidationMessage
from spdx.writer.rdf.annotation_writer import add_annotation_to_graph
from spdx.writer.rdf.creation_info_writer import add_creation_info_to_graph
from spdx.writer.rdf.extracted_licensing_info_writer import add_extracted_licensing_info_to_graph
from spdx.writer.rdf.file_writer import add_file_to_graph
from spdx.writer.rdf.package_writer import add_package_to_graph
from spdx.writer.rdf.relationship_writer import add_relationship_to_graph
from spdx.writer.rdf.snippet_writer import add_snippet_to_graph


def write_document_to_file(document: Document, file_name: str, validate: bool):
    if validate:
        validation_messages: List[ValidationMessage] = validate_full_spdx_document(document)
        if validation_messages:
            raise ValueError(f"Document is not valid. The following errors were detected: {validation_messages}")

    graph = Graph()
    doc_namespace = document.creation_info.document_namespace
    external_doc_ref_to_namespace: Dict[str, str] = {
        external_doc_ref.document_ref_id: external_doc_ref.document_uri
        for external_doc_ref in document.creation_info.external_document_refs
    }
    doc_node = add_creation_info_to_graph(document.creation_info, graph)
    for annotation in document.annotations:
        add_annotation_to_graph(annotation, graph, doc_namespace, external_doc_ref_to_namespace)

    for file in document.files:
        add_file_to_graph(file, graph, doc_namespace, external_doc_ref_to_namespace)

    for package in document.packages:
        add_package_to_graph(package, graph, doc_namespace, external_doc_ref_to_namespace)

    for relationship in document.relationships:
        add_relationship_to_graph(relationship, graph, doc_namespace, external_doc_ref_to_namespace)

    for snippet in document.snippets:
        add_snippet_to_graph(snippet, graph, doc_namespace, external_doc_ref_to_namespace)

    for extracted_licensing_info in document.extracted_licensing_info:
        add_extracted_licensing_info_to_graph(extracted_licensing_info, graph, doc_node, doc_namespace)

    graph = to_isomorphic(graph)
    graph.bind("spdx", SPDX_NAMESPACE)
    graph.bind("doap", DOAP)
    graph.bind("ptr", POINTER_NAMESPACE)
    graph.serialize(file_name, "pretty-xml", encoding="UTF-8", max_depth=100)

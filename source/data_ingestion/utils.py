import os
import json
from typing import Any
from rdflib import Graph, Namespace, Literal, RDF, XSD, URIRef, OWL, RDFS

from urllib.parse import quote


LINK_OPEN_SOURCE = True


def safe_uri_fragment(text: str) -> str:
    return quote(text.strip(), safe="")


def add_literal(g: Graph, subject: URIRef, predicate: URIRef, value: Any, datatype=XSD.string):
    if value:
        g.add((subject, predicate, Literal(str(value), datatype=datatype)))

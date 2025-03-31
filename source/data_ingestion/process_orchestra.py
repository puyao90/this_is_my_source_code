from data_enrichement.extra_api.search_api import search_and_link_artist
from constants import *
from utils import *


def link_orchestra(g: Graph, program_uri: URIRef, orchestra_name: str) -> URIRef:
    """Process orchestra entity with external linking"""
    if not orchestra_name:
        return None

    orchestra_uri = EXDATA[safe_uri_fragment(
        orchestra_name.lower().replace(" ", "-"))]
    g.add((orchestra_uri, RDF.type, EX.Orchestra))

    add_literal(g, orchestra_uri, RDFS.label, orchestra_name, XSD.string)

    # External linking logic
    search_and_link_artist(g, orchestra_uri, orchestra_name)

    g.add((program_uri, EX.orchestra_uri, orchestra_uri))
    return orchestra_uri

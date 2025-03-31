from data_enrichement.extra_api.search_api import search_and_link_artist
from constants import *
from utils import *


def process_soloist(g: Graph, work_uri: URIRef, soloist_data: dict, idx: int) -> URIRef:
    soloist_id = f"{work_uri.split('/')[-1]}-soloist-{idx}"
    soloist_uri = EXDATA[safe_uri_fragment(soloist_id)]
    g.add((soloist_uri, RDF.type, EX.Soloist))

    # Add soloist properties
    properties = [
        (EX.soloistName, "soloistName"),
        (EX.soloistInstrument, "soloistInstrument"),
        (EX.soloistRoles, "soloistRoles")
    ]

    for predicate, key in properties:
        add_literal(g, soloist_uri, predicate, soloist_data.get(key))
    if LINK_OPEN_SOURCE:
        search_and_link_artist(g, soloist_uri, soloist_data.get("soloistName"))

    g.add((work_uri, EX.hasSoloist, soloist_uri))
    return soloist_uri

from constants import *
from utils import *


def process_concert(g: Graph, program_uri: URIRef, concert_data: dict, idx: int) -> URIRef:
    """Process individual concert entity"""
    concert_id = f"{program_uri.split('/')[-1]}-concert-{idx}"
    concert_uri = EXDATA[safe_uri_fragment(concert_id)]
    g.add((concert_uri, RDF.type, EX.Concert))

    # Add concert properties
    properties = [
        (EX.eventType, "eventType"),
        (EX.Location, "Location"),
        (EX.Venue, "Venue"),
        (EX.Date, "Date"),
        (EX.Time, "Time")
    ]

    for predicate, key in properties:
        add_literal(g, concert_uri, predicate, concert_data.get(key))

    g.add((program_uri, EX.hasConcert, concert_uri))
    return concert_uri

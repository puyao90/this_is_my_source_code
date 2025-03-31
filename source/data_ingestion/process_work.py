from process_soloist import process_soloist
from constants import *
from utils import *
from data_enrichement.extra_api.search_api import search_and_link_artist, search_and_link_movement


def create_role_uri(work_uri: URIRef, role: str, idx: int = 1) -> URIRef:
    """Create URI for role entities (composer, conductor, movement)"""
    role_id = f"{work_uri.split('/')[-1]}-{role}-{idx}"
    return EXDATA[safe_uri_fragment(role_id)]


def process_work(g: Graph, program_uri: URIRef, work_data: dict, idx: int) -> URIRef:
    """Process musical work entity"""
    work_id = f"{program_uri.split('/')[-1]}-work-{idx}"
    work_uri = EXDATA[safe_uri_fragment(work_id)]
    g.add((work_uri, RDF.type, EX.Work))

    # Add basic work properties
    add_literal(g, work_uri, EX.workTitle, work_data.get("workTitle"))
    add_literal(g, work_uri, EX.interval, work_data.get("interval"))

    # Process movement with intermediate object
    if work_data.get("movement") and type(work_data.get("movement")) == str:
        add_literal(g, work_uri, EX.movementName, work_data["movement"])
        if LINK_OPEN_SOURCE:
            movement_uri = create_role_uri(work_uri, "movement")
            search_and_link_movement(g, movement_uri, work_data["movement"])
            g.add((movement_uri, RDF.type, EX.Movement))
            g.add((work_uri, EX.hasMovement, movement_uri))

    # Process composer with intermediate object
    if work_data.get("composerName"):
        add_literal(g, work_uri, EX.composerName,
                    work_data["composerName"])

        if LINK_OPEN_SOURCE:
            composer_uri = create_role_uri(work_uri, "composer")
            search_and_link_artist(g, composer_uri, work_data["composerName"])
            g.add((composer_uri, RDF.type, EX.Composer))
            g.add((work_uri, EX.hasComposer, composer_uri))

    # Process conductor with intermediate object
    if work_data.get("conductorName"):
        add_literal(g, work_uri, EX.conductorName,
                    work_data["conductorName"])
        if LINK_OPEN_SOURCE:
            conductor_uri = create_role_uri(work_uri, "conductor")
            g.add((conductor_uri, RDF.type, EX.Conductor))
            g.add((work_uri, EX.hasConductor, conductor_uri))

            search_and_link_artist(
                g, conductor_uri, work_data["conductorName"])

    # Process soloists
    for s_idx, soloist in enumerate(work_data.get("soloists", []), 1):
        if soloist:
            process_soloist(g, work_uri, soloist, s_idx)

    g.add((program_uri, EX.hasWork, work_uri))
    return work_uri

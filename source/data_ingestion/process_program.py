from constants import *
from utils import *
from process_orchestra import *
from process_concert import *
from process_work import *

# Schema
# root
# └── programs
#     └── program
#         ├── programID: string
#         ├── orchestra: string
#         ├── season: string
#         ├── concerts
#         │   └── concert
#         │       ├── eventType: string
#         │       ├── location: string
#         │       ├── Venue: string
#         │       ├── Date: dateTime
#         │       └── Time: string
#         └── works
#             └── work
#                 ├── ID: string
#                 ├── composerName: string (0..1)
#                 ├── workTitle: string (0..1)
#                 ├── movement: string (0..1)
#                 ├── conductorName: string (0..1)
#                 ├── soloists: string (0..1)
#                 └── interval: string (0..1)


def process_program(g: Graph, program_data: dict):
    program_id = program_data.get("programID")
    # print(f"Processing program ID: {program_id}")
    if not program_id:
        return

    # Create program entity
    program_uri = EXDATA[safe_uri_fragment(program_id)]
    # print(f"Program URI: {program_uri}")
    g.add((program_uri, RDF.type, EX.Program))
    add_literal(g, program_uri, EX.programID, program_data.get("programID"))
    add_literal(g, program_uri, EX.season, program_data.get("season"))
    add_literal(g, program_uri, EX.orchestra, "New York Philharmonic")

    # Process orchestra
    link_orchestra(g, program_uri, "New York Philharmonic")

    # Process concerts
    for idx, concert in enumerate(program_data.get("concerts", []), 1):
        process_concert(g, program_uri, concert, idx)

    # Process works
    for idx, work in enumerate(program_data.get("works", []), 1):
        process_work(g, program_uri, work, idx)

# webapp/entities.py
from dataclasses import dataclass, field
from typing import List, Optional
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON

# TTL
#  Sample data can be viewed in ./sample.ttl

# Configuration: Set to True to query from GraphDB server, False to query from file
USE_GRAPHDB_SERVER = True

# GraphDB server configuration
GRAPHDB_SERVER_URL = "http://localhost:7200/repositories/test1"

# Initialize graph
graph = Graph()
if not USE_GRAPHDB_SERVER:
    print("START PARSING")
    graph.parse('./output.ttl', format='turtle')
    print("FINISHED PARSING")

# Global query templates
SOLOIST_QUERY_TEMPLATE = """
PREFIX ex: <http://localhost:8000/schema#>
SELECT ?soloistInstrument ?soloistRoles ?soloistName
WHERE {{
    ?soloist a ex:Soloist ;
             ex:soloistInstrument ?soloistInstrument ;
             ex:soloistRoles ?soloistRoles ;
             ex:soloistName ?soloistName .
    FILTER(?soloistName = "{soloistName}")
}}
LIMIT 1
"""

WORK_QUERY_TEMPLATE = """
PREFIX ex: <http://localhost:8000/schema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX mo: <http://purl.org/ontology/mo/>
SELECT ?composerName ?workTitle ?movementName ?interval ?conductorName ?hasComposer ?recording
WHERE {{
    <{work_uri}> a ex:Work ;
                 ex:composerName ?composerName ;
                 ex:workTitle ?workTitle .
    OPTIONAL {{ <{work_uri}> ex:movementName ?movementName }}
    OPTIONAL {{ <{work_uri}> ex:interval ?interval }}
    OPTIONAL {{ <{work_uri}> ex:conductorName ?conductorName }}
    OPTIONAL {{ <{work_uri}> ex:hasComposer ?hasComposer }}
    OPTIONAL {{ <{work_uri}> mo:recording ?recording }}
}}
LIMIT 1
"""

SOLOIST_FOR_WORK_QUERY_TEMPLATE = """
PREFIX ex: <http://localhost:8000/schema#>
SELECT ?soloistName ?soloistInstrument ?soloistRoles
WHERE {{
    <{work_uri}> ex:hasSoloist ?soloist .
    ?soloist a ex:Soloist ;
             ex:soloistName ?soloistName ;
             ex:soloistInstrument ?soloistInstrument ;
             ex:soloistRoles ?soloistRoles .
}}
"""

CONCERT_QUERY_TEMPLATE = """
PREFIX ex: <http://localhost:8000/schema#>
SELECT ?eventType ?Location ?Venue ?Date ?Time
WHERE {{
    <{concert_uri}> a ex:Concert ;
                    ex:eventType ?eventType ;
                    ex:Location ?Location ;
                    ex:Venue ?Venue ;
                    ex:Date ?Date ;
                    ex:Time ?Time .
}}
LIMIT 1
"""

PROGRAM_QUERY_TEMPLATE = """
PREFIX ex: <http://localhost:8000/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?program ?orchestra ?season ?orchestra_uri ?orchestra_label
WHERE {{
    ?program a ex:Program ;
             ex:programID "{program_id}" ;
             ex:orchestra ?orchestra ;
             ex:orchestra_uri ?orchestra_uri ;
             ex:season ?season .
    ?orchestra_uri rdfs:label ?orchestra_label .
}}
LIMIT 1
"""

CONCERTS_FOR_PROGRAM_QUERY_TEMPLATE = """
PREFIX ex: <http://localhost:8000/schema#>
SELECT ?concert
WHERE {{
    <{program_uri}> ex:hasConcert ?concert.
}}
"""

WORKS_FOR_PROGRAM_QUERY_TEMPLATE = """
PREFIX ex: <http://localhost:8000/schema#>
SELECT ?work
WHERE {{
    <{program_uri}> ex:hasWork ?work .
    ?work a ex:Work .
}}
"""

WORK_ID_QUERY_TEMPLATE = """
PREFIX ex: <http://localhost:8000/schema#>
SELECT ?ID
WHERE {{
    <{work_uri}> ex:ID ?ID.
}}
LIMIT 1
"""

PROGRAM_LIST_QUERY = """
PREFIX ex: <http://localhost:8000/schema#>
SELECT DISTINCT ?programID ?season ?orchestra
WHERE {{
    ?program a ex:Program ;
             ex:programID ?programID ;
             ex:season ?season ;
             ex:orchestra ?orchestra .
}}
ORDER BY ?season ?programID
"""

PROGRAM_LIST_WITH_VENUE_QUERY = """
PREFIX ex: <http://localhost:8000/schema#>
SELECT DISTINCT ?programID ?season ?orchestra
WHERE {{
    ?program a ex:Program ;
             ex:programID ?programID ;
             ex:season ?season ;
             ex:orchestra ?orchestra ;
             ex:hasConcert ?concert .
    ?concert ex:Venue ?Venue .
   FILTER(REGEX(?Venue, "{Venue}", "i"))
}}
ORDER BY ?season ?programID
"""


def execute_query(query: str, params=None):
    print(f"Executing query: {query}")
    if USE_GRAPHDB_SERVER:
        sparql = SPARQLWrapper(GRAPHDB_SERVER_URL)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results["results"]["bindings"]
    else:
        return graph.query(query)


def list_program_ids():
    results = execute_query(PROGRAM_LIST_QUERY)
    return [
        (str(row['programID']['value']),
         str(row['season']['value']),
         str(row['orchestra']['value'])
         ) for row in results]


def list_program_ids_by_venue(venue):
    query = PROGRAM_LIST_WITH_VENUE_QUERY
    results = execute_query(query.format(Venue=venue))
    return [
        (str(row['programID']['value']),
         str(row['season']['value']),
         str(row['orchestra']['value'])
         ) for row in results]


@dataclass
class MusicArtist:
    """Base class for artists with MusicBrainz links"""
    uri: str  # Internal URI
    label: str
    mb_uri: Optional[str] = None  # MusicBrainz URI
    mb_name: Optional[str] = None
    mb_country: Optional[str] = None
    mb_disambiguation: Optional[str] = None


@dataclass
class Composer(MusicArtist):
    @staticmethod
    def get(composer_uri: str) -> Optional['Composer']:
        query = f"""
        PREFIX ex: <http://localhost:8000/schema#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX mo: <http://purl.org/ontology/mo/>
        PREFIX schema: <http://schema.org/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX exdata: <http://localhost:8000/>
        SELECT ?mb_uri ?mb_name ?mb_country ?mb_disambiguation
        WHERE {{
            exdata:{composer_uri.split('/')[-1]} a ex:Composer ;
                dc:creator ?mb_uri .
            ?mb_uri a mo:MusicArtist ;
                   foaf:name ?mb_name ;
                   schema:nationality ?mb_country ;
                   rdfs:comment ?mb_disambiguation .
        }}
        LIMIT 1
        """

        results = execute_query(query)
        for row in results:
            return Composer(
                uri=composer_uri,
                # Using MusicBrainz name as label
                label=str(row['mb_name']['value']),
                mb_uri=str(row['mb_uri']['value']),
                mb_name=str(row['mb_name']['value']),
                mb_country=str(row['mb_country']['value']),
                mb_disambiguation=str(row['mb_disambiguation']['value'])
            )
        return None


@dataclass
class Conductor(MusicArtist):
    @staticmethod
    def get(conductor_uri: str) -> Optional['Conductor']:
        query = f"""
        PREFIX ex: <http://localhost:8000/schema#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX mo: <http://purl.org/ontology/mo/>
        PREFIX schema: <http://schema.org/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX exdata: <http://localhost:8000/>
        SELECT ?mb_uri ?mb_name ?mb_country ?mb_disambiguation
        WHERE {{
            exdata:{conductor_uri.split('/')[-1]} a ex:Conductor ;
                dc:creator ?mb_uri .
            ?mb_uri a mo:MusicArtist ;
                   foaf:name ?mb_name ;
                   schema:nationality ?mb_country ;
                   rdfs:comment ?mb_disambiguation .
        }}
        LIMIT 1
        """

        results = execute_query(query)
        for row in results:
            return Conductor(
                uri=conductor_uri,
                # Using MusicBrainz name as label
                label=str(row['mb_name']['value']),
                mb_uri=str(row['mb_uri']['value']),
                mb_name=str(row['mb_name']['value']),
                mb_country=str(row['mb_country']['value']),
                mb_disambiguation=str(row['mb_disambiguation']['value'])
            )
        return None


@dataclass
class Orchestra:
    uri: str
    label: str


@dataclass
class Soloist:
    soloistName: str
    soloistInstrument: str
    soloistRoles: str

    @staticmethod
    def get(soloistName: str) -> Optional['Soloist']:
        query = SOLOIST_QUERY_TEMPLATE.format(soloistName=soloistName)
        results = execute_query(query)
        for row in results:
            return Soloist(
                soloistName=soloistName,
                soloistInstrument=str(row['soloistInstrument']['value']),
                soloistRoles=str(row['soloistRoles']['value'])
            )
        return None


@dataclass
class Movement:
    uri: str  # Internal URI (e.g., exdata:9297-work-4-movement-1)
    mb_movement_uri: Optional[str] = None  # MusicBrainz movement URI
    title: Optional[str] = None
    language: Optional[str] = None
    comment: Optional[str] = None
    composer: Optional[Composer] = None

    @staticmethod
    def get(movement_uri: str) -> Optional['Movement']:
        query = f"""
        PREFIX ex: <http://localhost:8000/schema#>
        PREFIX ns3: <http://purl.org/NET/c4dm/event.owl#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX mo: <http://purl.org/ontology/mo/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX exdata: <http://localhost:8000/>
        
        SELECT ?mb_movement ?title ?language ?comment ?composer
        WHERE {{
            exdata:{movement_uri.split('/')[-1]} a ex:Movement ;
                ns3:sub_event ?mb_movement .
            
            ?mb_movement a mo:Movement ;
                        dc:title ?title .
            OPTIONAL {{ ?mb_movement dc:language ?language }}
            OPTIONAL {{ ?mb_movement rdfs:comment ?comment }}
            OPTIONAL {{ ?mb_movement dc:creator ?composer }}
        }}
        LIMIT 1
        """

        results = execute_query(query)
        for row in results:
            # Get composer if available
            composer = None
            if 'composer' in row:
                composer = Composer.get(str(row['composer']['value']))

            return Movement(
                uri=movement_uri,
                mb_movement_uri=str(row['mb_movement']['value']),
                title=str(row['title']['value']) if 'title' in row else None,
                language=str(row['language']['value']
                             ) if 'language' in row else None,
                comment=str(row['comment']['value']
                            ) if 'comment' in row else None,
                composer=composer
            )
        return None


@dataclass
class Work:
    URI: str
    workTitle: str
    composer: Optional[Composer] = None
    conductor: Optional[Conductor] = None
    movement: Optional[Movement] = None  # Changed from str to Movement
    movement_name: Optional[str] = None  # Added to store movement name
    interval: Optional[str] = None
    recording_uri: Optional[str] = None
    soloists: List[Soloist] = field(default_factory=list)

    @staticmethod
    def get(work_uri: str) -> Optional['Work']:
        query = f"""
        PREFIX ex: <http://localhost:8000/schema#>
        PREFIX mo: <http://purl.org/ontology/mo/>
        PREFIX exdata: <http://localhost:8000/>
        SELECT ?workTitle ?composerName ?conductorName ?composerUri ?conductorUri ?movementName ?movementUri ?interval ?recording
        WHERE {{
            exdata:{work_uri.split('/')[-1]} a ex:Work ;
                        ex:workTitle ?workTitle .
            OPTIONAL {{ exdata:{work_uri.split('/')[-1]} ex:composerName ?composerName }}
            OPTIONAL {{ exdata:{work_uri.split('/')[-1]} ex:conductorName ?conductorName }}
            OPTIONAL {{ exdata:{work_uri.split('/')[-1]} ex:hasComposer ?composerUri }}
            OPTIONAL {{ exdata:{work_uri.split('/')[-1]} ex:hasConductor ?conductorUri }}
            OPTIONAL {{ exdata:{work_uri.split('/')[-1]} ex:movementName ?movementName }}
            OPTIONAL {{ exdata:{work_uri.split('/')[-1]} ex:hasMovement ?movementUri }}
            OPTIONAL {{ exdata:{work_uri.split('/')[-1]} ex:interval ?interval }}
            OPTIONAL {{ exdata:{work_uri.split('/')[-1]} mo:recording ?recording }}
        }}
        """

        results = execute_query(query)
        for row in results:
            # Get composer if exists
            composer = None
            if 'composerUri' in row:
                composer = Composer.get(str(row['composerUri']['value']))
                if not composer and 'composerName' in row:
                    # Create basic composer if only name is available
                    composer = Composer(
                        uri=str(row['composerUri']['value']),
                        label=str(row['composerName']['value'])
                    )

            # Get conductor if exists
            conductor = None
            if 'conductorUri' in row:
                conductor = Conductor.get(str(row['conductorUri']['value']))
                if not conductor and 'conductorName' in row:
                    # Create basic conductor if only name is available
                    conductor = Conductor(
                        uri=str(row['conductorUri']['value']),
                        label=str(row['conductorName']['value'])
                    )

            # Get movement if exists
            movement = None
            if 'movementUri' in row:
                movement = Movement.get(str(row['movementUri']['value']))

            return Work(
                URI=work_uri,
                workTitle=str(row['workTitle']['value']),
                composer=composer,
                conductor=conductor,
                movement=movement,
                movement_name=str(row.get('movementName', {}).get(
                    'value')) if 'movementName' in row else None,
                interval=str(row.get('interval', {}).get('value')
                             ) if 'interval' in row else None,
                recording_uri=str(row.get('recording', {}).get(
                    'value')) if 'recording' in row else None,
                soloists=[]
            )
        return None


@dataclass
class Link:
    event: str
    label: str
    startDate: str


@dataclass
class Concert:
    URI: str
    eventType: str
    Location: str
    Venue: str
    Date: str
    Time: str
    external_links: List[Link] = field(default_factory=list)

    def __post_init__(self):
        """
        Initialize external_links after object creation if venue is Carnegie Hall
        """
        print(">>>>>>>>>>>>>>>>")
        print(self.Date)
        print(self.Time)
        print(self.Venue)

        print(">>>>>>>>>>>>>>>>")
        if self.Venue != "Carnegie Hall" and self.Date is None:
            return

        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ns1: <http://schema.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?event ?label ?startDate
        WHERE {{
            ?event a ns1:Event ;
                ns1:startDate ?startDate ;
                rdfs:label ?label .

            FILTER(SUBSTR(STR(?startDate), 1, 10) = "{self.Date[:10]}")
        }}
        ORDER BY ?startDate
        """

        results = execute_query(query)
        self.external_links = [
            Link(
                event=str(row['event']['value']).replace(
                    "http://", "https://"),
                label=str(row['label']['value']),
                startDate=str(row['startDate']['value'])
            )
            for row in results
        ]

    @staticmethod
    def get(concert_uri: str) -> Optional['Concert']:
        query = CONCERT_QUERY_TEMPLATE.format(concert_uri=concert_uri)
        results = execute_query(query)
        for row in results:
            return Concert(
                URI=concert_uri,
                eventType=str(row.get('eventType', {}).get('value', '')),
                Location=str(row.get('Location', {}).get('value', '')),
                Venue=str(row.get('Venue', {}).get('value', '')),
                Date=str(row.get('Date', {}).get('value', '')),
                Time=str(row.get('Time', {}).get('value', ''))
            )
        return None


@dataclass
class Program:
    id: str
    programID: str
    orchestra: Orchestra  # Changed from orchestraName to Orchestra object
    season: str
    concerts: List[Concert] = field(default_factory=list)
    works: List[Work] = field(default_factory=list)

    @staticmethod
    def get(program_id: str) -> Optional['Program']:
        query = PROGRAM_QUERY_TEMPLATE.format(program_id=program_id)
        results = execute_query(query)
        for row in results:
            # Create Orchestra object from URI and label
            orchestra_uri = str(row['orchestra_uri']['value'])
            orchestra_label = str(row['orchestra_label']['value'])
            orchestra = Orchestra(
                uri=orchestra_uri,
                label=orchestra_label
            )

            prog = Program(
                id=str(row['program']['value']),
                programID=program_id,
                orchestra=orchestra,
                season=str(row['season']['value']),
                concerts=[],
                works=[]
            )

            # Query concerts using template
            concert_query = CONCERTS_FOR_PROGRAM_QUERY_TEMPLATE.format(
                program_uri=prog.id)
            for c_row in execute_query(concert_query):
                concert_uri = str(c_row['concert']['value'])
                concert = Concert.get(concert_uri)
                if concert:
                    prog.concerts.append(concert)

            # Query works using template
            work_query = WORKS_FOR_PROGRAM_QUERY_TEMPLATE.format(
                program_uri=prog.id)
            for w_row in execute_query(work_query):
                work_uri = str(w_row['work']['value'])
                work = Work.get(work_uri)
                if work:
                    prog.works.append(work)

            return prog
        return None


if __name__ == '__main__':
    program_id = "9297"
    program = Program.get(program_id)
    if program:
        print(program)
        for concert in program.concerts:
            print(concert)
        for work in program.works:
            print(work)
            for soloist in work.soloists:
                print(soloist)
    else:
        print(f"Program {program_id} not found.")

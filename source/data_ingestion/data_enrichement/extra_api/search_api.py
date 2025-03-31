from dataclasses import dataclass, field
from typing import Optional, List
import requests
import musicbrainzngs
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from rdflib.namespace import FOAF, DC, DCTERMS
import re

from .cache import cache

SCHEMA = Namespace("http://schema.org/")
MO = Namespace("http://purl.org/ontology/mo/")
EVENT = Namespace("http://purl.org/NET/c4dm/event.owl#")

LOG_FLAG = 0


def log_debug(message: str) -> None:
    """Print debug information if LOG_FLAG is enabled"""
    if LOG_FLAG:
        print(message)


@dataclass
class MBArtist:
    name: str
    id: str
    type: Optional[str] = None
    country: Optional[str] = None
    disambiguation: Optional[str] = None
    link: str = field(init=False)

    def __post_init__(self):
        self.link = f"https://musicbrainz.org/artist/{self.id}"


@dataclass
class MBMovement:
    title: str
    id: str
    type: Optional[str] = None
    language: Optional[str] = None
    disambiguation: Optional[str] = None
    composer: Optional[MBArtist] = None
    link: str = field(init=False)

    def __post_init__(self):
        self.link = f"https://musicbrainz.org/work/{self.id}"


@dataclass
class ArchiveItem:
    identifier: str
    title: Optional[str] = None
    creator: Optional[str] = None
    description: Optional[str] = None
    mediatype: Optional[str] = None
    collection: Optional[str] = None
    subject: Optional[str] = None
    link: str = field(init=False)

    def __post_init__(self):
        self.link = f"https://archive.org/details/{self.identifier}"


musicbrainzngs.set_useragent("Yao", "1.0", "py120990@gmail.com")


@cache()
def search_mb_artist(artist_name, limit=1):
    result = musicbrainzngs.search_artists(artist=artist_name, limit=limit)
    return [MBArtist(
        name=a.get('name', ''),
        id=a.get('id', ''),
        type=a.get('type'),
        country=a.get('country'),
        disambiguation=a.get('disambiguation')
    ) for a in result.get('artist-list', [])]


@cache()
def search_mb_movement(work_title, limit=1):
    result = musicbrainzngs.search_works(work=work_title, limit=limit)
    works = []
    for work in result.get('work-list', []):
        composer = None
        for relation in work.get('artist-relation-list', []):
            if relation.get('type') == 'composer':
                artist = relation.get('artist', {})
                composer = MBArtist(name=artist.get(
                    'name', ''), id=artist.get('id', ''))
                break
        works.append(MBMovement(
            title=work.get('title', ''),
            id=work.get('id', ''),
            type=work.get('type'),
            language=work.get('language'),
            disambiguation=work.get('disambiguation'),
            composer=composer
        ))
    return works


@cache()
def search_archive(query, field='creator', rows=1, page=1):
    archive_base_url = "https://archive.org/advancedsearch.php"
    params = {
        "q": f"{field}:{query}",
        "fl[]": ["identifier", "title", "creator", "description",
                 "mediatype", "collection", "subject"],
        "rows": rows,
        "page": page,
        "output": "json"
    }

    response = requests.get(archive_base_url, params=params)
    return [ArchiveItem(
        identifier=doc.get("identifier", ""),
        title=doc.get("title"),
        creator=doc.get("creator"),
        description=doc.get("description"),
        mediatype=doc.get("mediatype"),
        collection=doc.get("collection"),
        subject=doc.get("subject")
    ) for doc in response.json().get("response", {}).get("docs", [])]


def link_artist(g, entity, artist):
    artist_uri = URIRef(artist.link)
    g.add((artist_uri, RDF.type, MO.MusicArtist))
    g.add((artist_uri, FOAF.name, Literal(artist.name)))
    if artist.country:
        g.add((artist_uri, SCHEMA.nationality, Literal(artist.country)))
    if artist.disambiguation:
        g.add((artist_uri, RDFS.comment, Literal(artist.disambiguation)))
    g.add((entity, DC.creator, artist_uri))
    g.add((entity, MO.performer, artist_uri))


def clean_search_string(text: str) -> Optional[str]:
    if not text:
        return None
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    cleaned = cleaned.lower().strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    if len(cleaned) < 5:
        return None
    return cleaned if len(cleaned) >= 5 else None


def search_and_link_artist(g, entity, artist_name):
    if type(artist_name) is list:
        artist_name = ' '.join(artist_name)
    log_debug(f"Searching for artist: {artist_name}")
    cleaned_name = clean_search_string(artist_name)
    log_debug(f"Cleaned artist name: {cleaned_name}")
    if not cleaned_name:
        return

    artists = search_mb_artist(cleaned_name)
    if artists:
        link_artist(g, entity, artists[0])
    else:
        g.add((entity, DC.creator, Literal(artist_name)))


def search_and_link_movement(g, entity, movement_name):
    log_debug(f"Searching for movement: {movement_name}")
    cleaned_name = clean_search_string(movement_name)
    log_debug(f"Cleaned movement name: {cleaned_name}")
    if not cleaned_name:
        return

    movements = search_mb_movement(cleaned_name)
    archive_items = search_archive(cleaned_name, field='subject', rows=1)
    if archive_items:
        pass
        # print(f"Archive items: {archive_items}")
    movement_uri = None

    # Link MusicBrainz data
    if movements:
        movement = movements[0]
        movement_uri = URIRef(movement.link)

        # Add movement metadata
        g.add((movement_uri, RDF.type, MO.Movement))
        g.add((movement_uri, DC.title, Literal(movement.title)))
        if movement.language:
            g.add((movement_uri, DC.language, Literal(movement.language)))
        if movement.disambiguation:
            g.add((movement_uri, RDFS.comment, Literal(movement.disambiguation)))

        # Link to main entity
        g.add((entity, EVENT.sub_event, movement_uri))

        # Link composer if available
        if movement.composer:
            link_artist(g, movement_uri, movement.composer)

    # Link Archive.org data
    if archive_items:
        archive_item = archive_items[0]
        archive_uri = URIRef(archive_item.link)

        # Add recording metadata
        g.add((archive_uri, RDF.type, MO.Recording))
        g.add((archive_uri, DC.title, Literal(archive_item.title or movement_name)))
        if archive_item.creator:
            g.add((archive_uri, DC.creator, Literal(archive_item.creator)))
            # Try to find and link the creator in MusicBrainz
            search_and_link_artist(g, archive_uri, archive_item.creator)
        if archive_item.description:
            g.add((archive_uri, DC.description, Literal(archive_item.description)))
        if archive_item.subject:
            log_debug(f"Archive item subject: {archive_item.subject}")
            subjects = []
            if isinstance(archive_item.subject, str):
                subjects = [s.strip() for s in archive_item.subject.split(';')]
            elif isinstance(archive_item.subject, list):
                subjects = archive_item.subject

            for subject in subjects:
                if isinstance(subject, str):  # Additional safety check
                    g.add((archive_uri, DC.subject, Literal(subject.strip())))

        # Add collection info if available
        if archive_item.collection:
            # Handle collection whether it's a string or list
            collections = archive_item.collection
            if isinstance(collections, str):
                collections = [collections]

            # Create collection URIs
            for collection in collections:
                collection_uri = URIRef(
                    f"https://archive.org/details/{collection}")
                g.add((archive_uri, DCTERMS.isPartOf, collection_uri))
                g.add((collection_uri, RDF.type, MO.Collection))
                g.add((collection_uri, DC.title, Literal(collection)))

        # Link to movement or main entity
        target_uri = movement_uri if movement_uri else entity
        g.add((target_uri, MO.recording, archive_uri))

        # Add media type
        if archive_item.mediatype:
            g.add((archive_uri, DC.type, Literal(archive_item.mediatype)))

    # Fallback if no data found
    if not movements and not archive_items:
        g.add((entity, DC.title, Literal(movement_name)))


if __name__ == "__main__":
    g = Graph()
    g.bind('mo', MO)
    g.bind('event', EVENT)
    g.bind('schema', SCHEMA)
    test_entity = URIRef("http://example.org/concert/1")

    # When invovke this functions, it will search for the artist and movement on the MusicBrainz and Archive.org
    # The cache module, will automatically cache the results in the local disk, so we don't need to search again
    search_and_link_artist(g, test_entity, "Beethoven", )
    search_and_link_movement(g, test_entity, "Symphony No. 5")
    print(g.serialize(format='turtle'))

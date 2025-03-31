from rdflib import Graph, Namespace, Literal, RDF, XSD, URIRef, OWL, RDFS
from data_cleaning import DataFieldProcessor
from urllib.parse import quote

EX = Namespace("http://localhost:8000/schema#")
EXDATA = Namespace("http://localhost:8000/")

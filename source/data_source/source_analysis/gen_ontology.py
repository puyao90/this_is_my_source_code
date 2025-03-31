from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal, URIRef

# Namespaces
EX = Namespace("http://localhost:8001/terms#")
EXDATA = Namespace("http://localhost:8001/data#")

# Create a graph
g = Graph()

# Create a graph
g = Graph()

# Add namespaces
g.bind("ex", EX)
g.bind("owl", OWL)
g.bind("rdfs", RDFS)

# Define classes
g.add((EX.Program, RDF.type, OWL.Class))
g.add((EX.Concert, RDF.type, OWL.Class))
g.add((EX.Work, RDF.type, OWL.Class))
g.add((EX.Soloist, RDF.type, OWL.Class))
g.add((EX.Orchestra, RDF.type, OWL.Class))
g.add((EX.Composer, RDF.type, OWL.Class))

# Define object properties
g.add((EX.hasConcert, RDF.type, OWL.ObjectProperty))
g.add((EX.performedBy, RDF.type, OWL.ObjectProperty))
g.add((EX.heldAt, RDF.type, OWL.ObjectProperty))
g.add((EX.hasWork, RDF.type, OWL.ObjectProperty))
g.add((EX.hasSoloist, RDF.type, OWL.ObjectProperty))
g.add((EX.hasComposer, RDF.type, OWL.ObjectProperty))

# Define data properties
g.add((EX.date, RDF.type, OWL.DatatypeProperty))
g.add((EX.location, RDF.type, OWL.DatatypeProperty))
g.add((EX.composerName, RDF.type, OWL.DatatypeProperty))
g.add((EX.eventType, RDF.type, OWL.DatatypeProperty))
g.add((EX.venue, RDF.type, OWL.DatatypeProperty))
g.add((EX.time, RDF.type, OWL.DatatypeProperty))
g.add((EX.soloistInstrument, RDF.type, OWL.DatatypeProperty))
g.add((EX.soloistRoles, RDF.type, OWL.DatatypeProperty))

# Add descriptions
g.add((EX.Program, RDFS.label, Literal("Musical Program")))
g.add((EX.hasConcert, RDFS.label, Literal("has Concert")))

# Save to file
g.serialize("output.owl", format="xml")
print("Ontology saved as output.owl")

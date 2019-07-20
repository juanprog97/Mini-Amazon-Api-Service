from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client

db = GraphDatabase("http://172.18.0.2:7474", username="neo4j", password="admin")
q = "Match (s:User) where s.name='santigo2' return s"
# "db" as defined above
results = db.query(q, returns=(client.Node))
if(not results):
	print("HOL")
for r in results:
	print(r[0]["name"])
	for i in r:
		for j in i:
			print(i[j])

# The output:
# (Marco)-[likes]->(Punk IPA)
# (Marco)-[likes]->(Hoegaarden Rosee)


'''The query language for Neo4j is called Cypher.
It allows to describe patterns in graphs, in a declarative fashion, i.e. just like SQL,
you describe what you want, rather then how to retrieve it.
Cypher uses some sort of ASCII-art to describe nodes, relationships and their direction.'''

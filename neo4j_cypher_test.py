from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client

db = GraphDatabase("http://172.17.0.2:7474", username="neo4j", password="admin")
q = "Match(b:User)-[d:Customer]->(s:User) where b.name='andrea10' and s.name='santigo2' set d.rate = '4.9'"
# "db" as defined above
results = db.query(q, returns=(client.Node,client.Relationship,client.Node,str))

q = "Match(b:User)-[d:Customer]->(s:User) where d.id=1 return b,d,s"
results = db.query(q, returns=(client.Node,client.Relationship,client.Node,str))
print({"buyer":{'name':results[0][0]['name'],'id':results[0][0]['id']},"sale":{'id':results[0][1]['id'],'rate':results[0][1]['rate']},
            "seller":{'id':results[0][2]['id'],'name':results[0][2]['name']}  })
#print("(%s)-[id:%s]->(%s)"%(results[0]['name'],results[1],results[2]['name']))

# The output:
# (Marco)-[likes]->(Punk IPA)
# (Marco)-[likes]->(Hoegaarden Rosee)


'''The query language for Neo4j is called Cypher.
It allows to describe patterns in graphs, in a declarative fashion, i.e. just like SQL,
you describe what you want, rather then how to retrieve it.
Cypher uses some sort of ASCII-art to describe nodes, relationships and their direction.'''

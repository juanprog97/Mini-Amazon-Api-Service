from flask_restplus import Api, Resource, fields
from flask import Flask, request, Response
import json
import os
import socket
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import datetime



app = Flask(__name__)

api = Api(
    app,
    version='1.0.0',
    title='Users API',
    description='A simple Users API',
)

ns = api.namespace('users', description='Users operations')
ps = api.namespace('product', description='Product operations')
cs = api.namespace('customer', description='Customer operations')

db = GraphDatabase("http://172.18.0.2:7474", username="neo4j", password="admin")
#q = 'match (n:User) return n.name, n.password, n.active, n.id'
#results = db.query(q, returns=(client.Node, str, client.Node))


product = api.model('Product',{
        'id':fields.Integer(readOnly=True,description='The product unique identifier'),
        'productName': fields.String(required=True,description="Name of Product"),
        'quantity': fields.String(required=True,description="Quantity in stock"),
        'Department': fields.String(required=True,description='Department of Products'),
        'Category': fields.String(required=True,description="Category of Products"),
        'SubCategory':fields.String(required=True,description="SubCategory of Products")
})

user = api.model('User',{
        'id':fields.Integer(readOnly=True,description='The user unique idenfitifier'),
        'active':fields.Integer(required=True,description="The identifier which tells if the user is active"),
        'name':fields.String(required=True,description="The name of the user"),
        'password':fields.String(required=True,description="The password of the user")
})

customer = api.model('Customer',{
        'id':fields.Integer(readOnly=True,description='The product unique identifier'),
        'buyer':fields.String(required=True,description="The buyer of the product"),
        'seller':fields.String(required=True,description="The seller of the product"),
        'starts':fields.String(required=True,description="Purchase score")
})


class CustomertDAO(object):
     def __init__(self):
         self.counter = 0
         self.query = ''

     def create(self,buyer,seller,rate):
         self.counter += 1
         self.query = "Match(b:User) where b.name = '%s' return b" %(buyer)
         n_buyer = db.query(self.query, returns=(client.Node))
         self.query = "Match(s:User) where s.name = '%s' return s" %(seller)
         n_seller = db.query(self.query, returns=(client.Node))
         if(len(n_buyer)==0):
             api.abort(404, "Buyer {} doesn't exist".format(buyer))
         if(len(n_seller)==0):
             api.abort(404, "Seller {} doesn't exist".format(seller))
         self.query ="Match(b:User),(s:User) where b.name ='%s' and s.name = '%s' Create(b)-[:Customer {rate:'%s',id:%d}]->(s)" %(buyer,seller,rate,self.counter)
         results = db.query(self.query)
         self.query = "Match(b:User)-[d:Customer]->(s:User) where b.name = '%s' and s.name='%s' and d.id= %d return b,d,s" %(buyer,seller,self.counter)
         results= db.query(self.query, returns=(client.Node,client.Relationship,client.Node,str))
         change_new = {"buyer":results[0][0]['name'],'starts':results[0][1]['rate'],'id':results[0][1]['id'],"seller":results[0][2]['name']}
         return change_new

     def update(self,buyer,seller,rate):
          self.query = "Match(b:User) where b.name = '%s' return b" %(buyer)
          n_buyer = db.query(self.query, returns=(client.Node))
          self.query = "Match(s:User) where s.name = '%s' return s" %(seller)
          n_seller = db.query(self.query, returns=(client.Node))
          if(len(n_buyer)==0):
              api.abort(404, "Buyer {} doesn't exist".format(buyer))
          if(len(n_seller)==0):
              api.abort(404, "Seller {} doesn't exist".format(seller))
          self.query = "Match(b:User)-[d:Customer]->(s:User) where b.name='%s' and s.name='%s' set d.rate = '%s'"%(buyer,seller,rate)
          results = db.query(self.query)
          self.query = "Match(b:User)-[d:Customer]->(s:User) where b.name = '%s' and s.name= '%s' return b,d,s" %(buyer,seller)
          results= db.query(self.query, returns=(client.Node,client.Relationship,client.Node,str))
          change_new = {"buyer":results[0][0]['name'],'starts':results[0][1]['rate'],'id':results[0][1]['id'],"seller":results[0][2]['name']}
          return change_new


class UserDAO(object):
    def __init__(self):
        self.counter = 500
        self.query = ""

    def get(self, username):
        '''Returns a list of users with that username'''
        self.query = "match (u:User) where u.name='%s' return u"%(username)
        q = db.query(self.query, returns=(client.Node))
        if(len(q)==0):
            api.abort(404, "User {} doesn't exist".format(username))
        result = {"active":q[0][0]['active'],'id':q[0][0]['id'],'name':q[0][0]['name'],"password":q[0][0]['password']}
        return result

    def create(self, username,password,active):
        '''Returns a list of users with that username'''
        self.query = "MATCH (u:User) where u.name='%s' return u"%(username)
        q = db.query(self.query, returns=(client.Node))
        if(len(q)!=0):
            api.abort(404, "User {} already exist".format(username))
            result = {"active":q[0][0]['active'],'id':q[0][0]['id'],'name':q[0][0]['name'],"password":q[0][0]['password']}
        self.query = "CREATE (u:User {active:'%s',id:'%s',name:'%s',password:'%s'}) "%(active,self.counter,username,password)
        self.counter += 1
        q = db.query(self.query, returns=(client.Node))
        result = {"active":'{}'.format(active),'name':'{}'.format(username),"password":'{}'.format(password)}
        return result

    def update(self, username,password,active):
        '''Returns a list of users with that username'''
        self.query = "MATCH (u:User) where u.name='%s' return u"%(username)
        q = db.query(self.query, returns=(client.Node))
        if(len(q)==0):
            api.abort(404, "User {} doesn't exist".format(username))
        results = []
        result = {"active":q[0][0]['active'],'id':q[0][0]['id'],'name':q[0][0]['name'],"password":q[0][0]['password']}
        results.append(result)
        self.query = "MATCH (u:User) where u.name='%s' set u.password='%s', u.active=%s return u "%(username,password,active)
        q = db.query(self.query, returns=(client.Node))
        results.append({"active":q[0][0]['active'],'id':q[0][0]['id'],'name':q[0][0]['name'],"password":q[0][0]['password']})
        return results

    def delete(self, username):
        '''Returns a list of users with that username'''
        self.query = "MATCH (u:User) where u.name='%s' return u"%(username)
        q = db.query(self.query, returns=(client.Node))
        if(len(q)==0):
            api.abort(404, "User {} doesn't exist".format(username))
        result = {"active":q[0][0]['active'],'id':q[0][0]['id'],'name':q[0][0]['name'],"password":q[0][0]['password']}
        self.query = "MATCH (u:User) where u.name='%s' DETACH DELETE u"%(username)
        q = db.query(self.query, returns=(client.Node))
        return result


class ProductDAO(object):
    def __init__(self):
        self.counter = 0
        self.query = ""


    def get(self, id):
        '''Returns a list of users with that username'''
        self.query = "match (p:Product) where u.id='%s' return p"%(id)
        q = db.query(self.query, returns=(client.Node))
        if(len(q)==0):
            api.abort(404, "Product doesn't exist")
        result = {'id':q[0][0]['id'],"name":q[0][0]['name'],'quantity':q[0][0]['quantity']}
        return result

    def create(self, productname,quantity,department,category,subcategory):
        '''Returns a list of users with that username'''
        self.query = "MATCH (a:Department)<-[:Category]-(b:Category)<-[:SubCategory]-(c:SubCategory)<-[:Product]-(p:Product) where a.name='%s' and b.name='%s' and c.name='%s' and p.name='%s' return p"%(department,category,subcategory,productname)
        q = db.query(self.query, returns=(client.Node))
        if(len(q)!=0):
            api.abort(404, "Product {} already exist".format(productname))
        self.query = "MATCH (a:Department)<-[:Category]-(b:Category)<-[:SubCategory]-(c:SubCategory) where a.name='%s' and b.name='%s' and c.name='%s' CREATE (p:Product { id:'%s' , name:'%s' ,quantity:'%s' })-[:Product]->(c)"%(department,category,subcategory,self.counter,productname,quantity)
        self.counter += 1
        q = db.query(self.query)
        result = {'id':5 ,'productname':'','quantity':'','department':'','category':'','subcategory':''}
        return result

    def update(self, idProduct, productname,quantity):
        '''Returns a list of users with that username'''
        self.query = "MATCH (p:Product) where p.id=%s return p"%(idProduct)
        q = db.query(self.query, returns=(client.Node))
        if(len(q)==0):
            api.abort(404, "Product {} doesn't exist".format(idProduct))
        self.query = "MATCH (p:Product) where p.id='%s' SET p.name='%s', p.quantity='%s' "%(idProduct,productname,quantity)
        q = db.query(self.query)
        result = {'id':0 ,'productname':'','quantity':'','department':'','category':'','subcategory':''}
        return result

    def delete(self, idProduct):
        '''Returns a list of users with that username'''
        self.query = "MATCH (p:Product) where p.id='%s' return p"%(idProduct)
        q = db.query(self.query, returns=(client.Node))
        if(len(q)==0):
            api.abort(404, "Product {} doesn't exist".format(idProduct))
        self.query = "MATCH (p:Product) where p.id='%s' DETACH DELETE p"%(idProduct)
        q = db.query(self.query, returns=(client.Node))
        result = {'id':0 ,'productname':'','quantity':'','department':'','category':'','subcategory':''}
        return result


DAO = UserDAO()
DAOP =  ProductDAO()
DAOC = CustomertDAO()





@ps.route('/<string:productname>/<string:quantity>/<string:department>/<string:category>/<string:subcategory>')
@ps.response(404, 'User already exists')
@ps.param('productname', 'The product identifier')
@ps.param('quantity', 'The quantity of products')
@ps.param('department', "Product's department")
@ps.param('category', "Product's category")
@ps.param('subcategory', "Product's subcategory")
class ProductList(Resource):
    '''Shows a list of all products, and lets you POST to add new products'''

    @ps.doc('create_product')
    @ps.expect(product)
    @ps.marshal_with(product, code=201)
    def post(self,productname,quantity,department,category,subcategory):
        '''Create a new product'''
        return DAOP.create(productname,quantity,department,category,subcategory), 201

@ps.route('/<string:idProduct>/<string:productname>/<string:quantity>')
@ps.response(404, 'User already exists')
@ps.param('idProduct', 'The product identifier')
@ps.param('productname', 'The product identifier')
@ps.param('quantity', 'The quantity of products')
class ProductList(Resource):
    '''Shows a list of all products, and lets you POST to add new products'''

    @ps.doc('update_product')
    @ps.expect(product)
    @ps.marshal_with(product, code=201)
    def put(self, idProduct, productname,quantity):
        '''Update a product given its identiproductnamefier'''
        return DAOP.update(idProduct, productname,quantity)

@ps.route('/<string:idProduct>')
@ps.response(404, 'Product not found')
@ps.param('productname', 'The productname identifier')
class Product(Resource):
    '''Show a single product item and lets you delete them'''

    @ps.doc('get_product')
    @ps.marshal_with(product)
    def get(self, idProduct):
        '''Fetch a given resource'''
        return DAOP.get(idProduct)

    @ps.doc('delete_product')
    @ps.response(204, 'Product deleted')
    def delete(self, idProduct):
        '''Delete a product given its productname'''
        DAOP.delete(idProduct)
        return '', 204



@ns.route('/<string:username>/<string:password>/<string:active>')
@ns.response(404, 'User not found')
@ns.param('username', 'The username')
@ns.param('password', 'The password')
@ns.param('active', 'If the user is active select 1 otherwhise 0')
class CreateUser(Resource):
    '''Shows a list of all users, and lets you POST to add new users'''

    @ns.doc('create_user')
    @ns.expect(user)
    @ns.marshal_with(user, code=201)
    def post(self,username,password,active):
        '''Create a new user'''
        return DAO.create(username,password,active), 201

    @ns.doc('update_user')
    @ns.expect(user)
    @ns.marshal_with(user, code=201)
    def put(self, username,password,active):
        '''Update a user given its identiusernamefier'''
        return DAO.update(username,password,active)


@ns.route('/<string:username>')
@ns.response(404, 'User not found')
@ns.param('username', 'The username identifier')
class User(Resource):
    '''Show a single user item and lets you delete them'''

    @ns.doc('get_user')
    @ns.marshal_with(user)
    def get(self, username):
        '''Fetch a given resource'''
        return DAO.get(username)

    @ns.doc('delete_user')
    @ns.response(204, 'User deleted')
    def delete(self, username):
        '''Delete a user given its username'''
        DAO.delete(username)
        return '', 204

    

@cs.route('/<string:buyer>/salesperson/<string:seller>/start/<string:rate>')
@cs.response(404,'User not found')
@cs.param('buyer','The buyer identifier')
@cs.param('seller','The buyer identifier')
@cs.param('rate','Rated of sale')
class Customer(Resource):
    '''Post to add new sale and Put to change value of rate'''
    @cs.doc('Create a new sale')
    @cs.expect(customer)
    @cs.marshal_with(customer)
    def post(self,buyer,seller,rate):
        '''Create a new sale'''
        return DAOC.create(buyer,seller,rate)
    @cs.expect(customer)
    @cs.marshal_with(customer)
    def put(self,buyer,seller,rate):
        '''Update a sale given its two identiusernamefier'''
        return DAOC.update(buyer,seller,rate)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9090, debug=True)

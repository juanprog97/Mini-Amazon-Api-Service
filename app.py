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
user = api.model('User', {
    'id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'username': fields.String(required=True, description='The username'),
    'status': fields.String(required=True, description='The status')
})

db = GraphDatabase("http://172.17.0.2:7474", username="neo4j", password="admin")
#q = 'match (n:User) return n.name, n.password, n.active, n.id'
#results = db.query(q, returns=(client.Node, str, client.Node))


product = api.model('Product',{
        'id':fields.Integer(readOnly=True,description='The product unique identifier'),
        'Department': fields.String(required=True,description='Department of Products'),
        'Category': fields.String(required=True,description="Category of Products"),
        'SubCategory':fields.String(required=True,description="SubCategory of Products"),
        'Active': fields.Integer(required=True,description="Status of Product"),
        'nameProduct': fields.String(required=True,description="Name of Product"),
        'rate':fields.Float(required=True,description="rate of Product"),
        'createDate': fields.String(required=False,description="Date of Creation"),
        'country': fields.String(required=True,description="Country of Creation")
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
        self.counter = 0
        self.users = []

    def get(self, username):

        for user in results:
            if user['name'] == username:
                return user
        api.abort(404, "User {} doesn't exist".format(username))

    def create(self, data):
        new_user = data
        new_user['id'] = self.counter = self.counter + 1
        self.users.append(new_user)
        return new_user

    def update(self, username, data):
        user = self.get(username)
        user.update(data)
        return user

    def delete(self, username):
        user = self.get(username)
        self.users.remove(user)


class ProductDAO(object):
    def __init__(self):
        self.counter = 0
        self.products = []


    def get(self,product):
        for prod in self.product:
            if prod['nameProduct'] == product:
                return prod
        api.abort(404, "Product {} doesn't exist".format(product))

    def create(self,data):
        new_product = data
        new_product['id'] = self.counter = self.counter + 1
        new_product['createDate'] = datetime.date.today()
        self.product.append(new_product)
        return new_product
    def update(self,prod,data):
        product = self.get(prod)
        product.update(data)
        return product
    def delete(self,prod):
        product = self.get(prod)
        self.products.remove(product)


DAO = UserDAO()
DAOP =  ProductDAO()
DAOC = CustomertDAO()





@ps.route("/")
class ProductList(Resource):
    '''Shows a list of all products, and lets you POST to add new products'''

    @ps.doc('list_products')
    @ps.marshal_list_with(product)
    def get(self):
        '''List all products'''
        return DAOP.products

    @ps.doc('create_product')
    @ps.expect(product)
    @ps.marshal_with(product, code=201)
    def post(self):
        '''Create a new product'''
        return DAOP.create(api.payload), 201


@ps.route('/<string:productname>')
@ps.response(404, 'Product not found')
@ps.param('productname', 'The productname identifier')
class Product(Resource):
    '''Show a single product item and lets you delete them'''

    @ps.doc('get_product')
    @ps.marshal_with(product)
    def get(self, productname):
        '''Fetch a given resource'''
        return DAOP.get(productname)

    @ps.doc('delete_product')
    @ps.response(204, 'Product deleted')
    def delete(self, productname):
        '''Delete a product given its productname'''
        DAOP.delete(productname)
        return '', 204

    @ps.expect(product)
    @ps.marshal_with(product)
    def put(self, productname):
        '''Update a product given its identiproductnamefier'''
        return DAOP.update(productname, api.payload)







@ns.route("/")
class UsersList(Resource):
    '''Shows a list of all users, and lets you POST to add new users'''

    @ns.doc('list_users')
    @ns.marshal_list_with(user)
    def get(self):
        '''List all users'''
        return DAO.users

    @ns.doc('create_user')
    @ns.expect(user)
    @ns.marshal_with(user, code=201)
    def post(self):
        '''Create a new user'''
        return DAO.create(api.payload), 201


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

    @ns.expect(user)
    @ns.marshal_with(user)
    def put(self, username):
        '''Update a user given its identiusernamefier'''
        return DAO.update(username, api.payload)

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

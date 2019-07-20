from neo4jrestclient.client import GraphDatabase
db = GraphDatabase("http://172.18.0.2:7474", username="neo4j", password="admin")

def main():

    #Add User
    print("\nAddUser\n")
    data = open("./Datos/usr.txt", "r")
    node = db.labels.create("User")
    cont= 1
    data.readline()
    users = data.readline().strip().split(" ")
    while(len(users) != 1):
        datUser,datPass,datActive = users[0],users[1],users[2]
        userNew = db.nodes.create(name=datUser,password=datPass,active=datActive,id=cont)
        users = data.readline().strip().split(" ")
        print("*ADD, User:{0}, Password:{1}, Active:{2}".format(datUser,datPass,datActive))
        node.add(userNew)
        cont+=1

    #CreateDepartaments
    print("\nCreate Departaments\n")
    data = open("./Datos/departamentos.txt", "r")
    node = db.labels.create("Department")
    nodeCat = db.labels.create("Category")
    nodeSub = db.labels.create("SubCategory")
    cont = 1
    data.readline()
    listDepat = ["Book","Coche y Moto","Computadores","Digital Music","Electronics","Industrial&Scientific","Kitchen&Home"
                 "Luggage","Movies&TV","Music,CDs & Vinyl","SportAndOutdoors","ToysAndGames"
                ]
    depar = data.readline().strip().split("|")
    while(len(depar) != 1):
        datId, datName,datActive,dataCreateDate,datCountry = depar[0],depar[1],depar[2],depar[3],depar[4]
        depaNew = db.nodes.create(name=datName,id=datId,active=datActive,create_date=dataCreateDate,country=datCountry)
        depar = data.readline().strip().split("|")
        print("*Add,id:{0}, Departaments:{1},Active:{2},CreateDate:{3},Country:{4}".format(datId,datName,datActive,dataCreateDate,datCountry))
        node.add(depaNew)
        if(datActive != '0'):
            DataDep = open(f"./Datos/{datName}.txt", "r")
            DataDep.readline()
            firstLe =""
            while(True):
                 dat = DataDep.readline().strip().split("|")
                 if(len(dat) == 1):
                     break
                 else:
                     if(firstLe != dat[2]):
                         firstLe = dat[2]
                         cate = db.nodes.create(name=firstLe)
                         nodeCat.add(cate)
                         cate.relationships.create("Category",depaNew)
                         print("\n*Add,Category:{0}-----\n".format(firstLe))

                     else:
                        subCa = db.nodes.create(name=dat[3],active=dat[4],createDate=dat[5],country=dat[6])
                        nodeSub.add(subCa)
                        subCa.relationships.create("SubCategory",cate)
                        print("*Add,SubCategory:{0},Active:{1},Create Date:{2},Country:{3}".format(dat[3],dat[4],dat[5],dat[6]))

main()

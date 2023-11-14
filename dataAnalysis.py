import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import networkx as nx
import sqlite3
class DataAnalysis():

    def __init__(self,dbName):
        self.dbName = dbName

    def getKeysMainUser(self):
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        c.execute("""SELECT dbID FROM userData WHERE fromMainUser = True """)
        keys = c.fetchall()
        returnKeys = []
        for followerKeys in keys:
            returnKeys.append(followerKeys[0])
        conn.close()
        return returnKeys

    def getFollowers(self,beingFollowed):
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        c.execute("""SELECT follower FROM whoFollowsWho WHERE beingFollowed=? """,(str(beingFollowed),))
        followers = c.fetchall()
        returnKeys = []
        conn.close()
        if len(followers) != 0:
            for i in followers:
                returnKeys.append(i[0])
            return returnKeys
        else:
            return None

    def getFollowings(self,following):
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        c.execute("""SELECT beingFollowed FROM whoFollowsWho WHERE follower=? """,(str(following),))
        followers = c.fetchall()
        returnKeys = []
        conn.close()
        if len(followers) != 0:
            for i in followers:
                returnKeys.append(i[0])
            return returnKeys
        else:
            return None

    def getAllUsersDb(self):
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        c.execute("""SELECT dbID FROM userData""")  #Get all users this time to be able to add them to the nodes
        keys = c.fetchall()
        returnKeys = []
        for followerKeys in keys:
            returnKeys.append(followerKeys[0])
        conn.close()
        print(returnKeys)
        return returnKeys


    def removeInferiorNode(self,Graph,connectionThreshold):
        toBeRemoved = []
        for node in Graph.nodes():
            if len(Graph.edges(node)) <=connectionThreshold:  #Wenn nur eine Verbidnug beseteht wird die Node aus dem Graphen geworfen
                toBeRemoved.append(node)
        for node in toBeRemoved:
            Graph.remove_node(node)
        print("Left Nodes")
        print(Graph.nodes())
        for node in Graph.nodes():
            print(node, len(Graph.edges(node)))

    def networkGraph(self,mode=0,connectionThreshold=0):  #Wenn mode=0 Dann wird mit being Followed gematcht, bei mode=1 wird die Anfrage an DB geändert und die following spalte wird abgefragt und angeglichen
        print("Graphics Output")
        G=nx.Graph()
        keysInDb = self.getAllUsersDb() #Get every user first so you are able to create the nodes to the mainUsers Followers
        for key in keysInDb:
            try:
                img = mpimg.imread('pictures/'+str(key)+'Alpha.png')
            except Exception:
                img = mpimg.imread('pictures/0Alpha.png')
            G.add_node(key, image=img)
        print(G.nodes())
        keysList = self.getKeysMainUser()
        if mode == 0:
            for keys in keysList:   #Main Users List
                print(keys)
                followers = self.getFollowers(keys)
                if followers != None:
                    for follower in followers:
                        G.add_edge(keys, follower)
            self.removeInferiorNode(G,connectionThreshold)
        else:
            for keys in keysList:   #Main Users List
                print(keys)
                followings = self.getFollowings(keys)
                if followings != None:
                    for follower in followings:
                        G.add_edge(keys, follower)
            self.removeInferiorNode(G,connectionThreshold)
        #pos=nx.planar_layout(G)
        #pos = nx.spiral_layout(G)
        print(G.edges())
        pos = nx.spring_layout(G,k=0.5,iterations=20,scale=1.7)       #Man selbst in der Mitte und die anderen außenrum
        fig=plt.figure(figsize=(100,100))
        ax=plt.subplot(111)
        ax.set_aspect('equal')
        nx.draw_networkx_edges(G,pos,ax=ax)

        plt.xlim(-1.5,1.5)
        plt.ylim(-1.5,1.5)

        trans=ax.transData.transform
        trans2=fig.transFigure.inverted().transform

        piesize=0.02 # this is the image size
        p2=piesize/2.0
        for n in G:
            xx,yy=trans(pos[n]) # figure coordinates
            xa,ya=trans2((xx,yy)) # axes coordinates
            a = plt.axes([xa-p2,ya-p2, piesize, piesize])
            a.set_aspect('equal')
            try:
                a.imshow(G.nodes[n]['image'])
            except Exception:
                print("Something went wrong")
            a.axis('off')
        ax.axis('off')
        plt.savefig("NAME OF EXPORTED GRAPH")


    def networkGraphText(self,mode=0,connectionThreshold=0):
        print("Graph Text")
        G = nx.Graph()
        keysInDb = self.getAllUsersDb()  # Get every user first so you are able to create the nodes to the mainUsers Followers
        for key in keysInDb:
            G.add_node(key)
        print(G.nodes())
        keysList = self.getKeysMainUser()
        if mode == 0:
            for keys in keysList:  # Main Users List
                print(keys)
                followers = self.getFollowers(keys)
                if followers != None:
                    for follower in followers:
                        G.add_edge(keys, follower)
            self.removeInferiorNode(G, connectionThreshold)
        else:
            for keys in keysList:  # Main Users List
                print(keys)
                followings = self.getFollowings(keys)
                if followings != None:
                    for follower in followings:
                        G.add_edge(keys, follower)
            self.removeInferiorNode(G, connectionThreshold)
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        for node in G.nodes():
            c.execute("""UPDATE userData SET picNeeded = ? WHERE dbID = ?""",(True,node,))
        conn.commit()
        conn.close()



#dataObject = DataAnalysis("1584477531.db")
#dataObject = DataAnalysis("samuel.db")

#keys = dataObject.getKeysMainUser()
#for key in keys:
#    print(dataObject.getFollowers(key))

#dataObject.getAllUsersDb()
#Wenn man eine Zahl(Int) übergibt als 2. Parameter werden alle Follower die threshold<=Zahl Connections haben aus dem Graphen geworfen (Standardmäßig 0 damit keiner verloren geht)
#dataObject.networkGraph(0,1)# Bei 00, 10 mode=0, Bei 11, 01 mode=1 -> Dies bezieht sich auf den Vorherigen schritt er DatenAggregation weil sich der Aufbau der Datenbank dadurch verändert.



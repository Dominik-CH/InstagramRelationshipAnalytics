#https://github.com/realsirjoe/instagram-scraper/
from igramscraper.exception import InstagramException
from igramscraper.instagram import Instagram
from time import sleep
import time
import os
import requests
import sqlite3
import sys
import random
from config import USERNAME, PASSWORD, MAINPASSWORD, MAINUSERNAME
from dataAnalysis import DataAnalysis
from PIL import Image, ImageDraw, ImageFilter


class ModifiedInsta(Instagram):

    def __init__(self):
        Instagram.__init__(self)
        self.dbName = None

    def downloadProfilePicture(self,url, name):
        if not os.path.exists("pictures"):
            os.makedirs("pictures")
        response = requests.get(url)
        # picture = open(name+".jpg","wb")
        # picture.write(response.content)
        # picture.close()
        with open(os.path.join("pictures", name + ".jpg"), 'wb') as temp_file:
            temp_file.write(response.content)

    def listMostRecentFollowers(self,maxInList=30,username=None,userID=None):   #Zeigt die Follower an die dir am aktuellsten folgen
        followers = []
        if (username==None) and (userID == None):
            print("Username oder ID müssen angegeben werden")
            return False
        if userID == None:
            try:
                account = instagram.get_account(username)
                sleep(1)
                followers = instagram.get_followers(account.identifier, maxInList+100, 100, delayed=True,
                                                maxInList=maxInList)  # Get 150 followers of 'kevin', 100 a time with random delay between requests
                userID = account.identifier
            except InstagramException as ex:
                if ex.args[0][-3:] == "403":
                    print("User is private. Skipping User")
                else:
                    print("Unknown error")
                    print(ex)
                    sys.exit(1)
            except Exception:
                print("Something went wrong")
        elif username == None:
            try:
                sleep(1)
                followers = instagram.get_followers(userID, maxInList+100, 100, delayed=True,   #Die +100 ist nötig, da sonst die pageSize kleiner sein könnte als der count
                                            maxInList=maxInList)  # Get 150 followers of 'kevin', 100 a time with random delay between requests
            except InstagramException as ex:
                if ex.args[0][-3:] == "403":
                    print("User is private. Skipping User")
                else:
                    print("Unknown error")
                    print(ex)
                    sys.exit(1)
            except Exception:
                print("Something went wrong")
        try:
            self.createDbEntryFollowers(followers["accounts"])
            self.matchFollowersToBeingFollowed(userID,followers["accounts"])
            self.setScrapedTrue(userID)
        except Exception as e:
            print(e)
            print("Something went wrong")
            print(followers)


    def setScrapedTrue(self,instaID):
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        c.execute("""UPDATE userData SET scraped = ? WHERE instaID = ?""", (True,instaID,))
        conn.commit()
        conn.close()

    def listMostRecentFollowing(self,maxInList=30,username=None,userID=None):   #Zeigt die Liste der Personen denen ein user seit kürzester Zeit folgt
        followings = []
        if (username==None) and (userID == None):
            print("Username oder ID müssen angegeben werden")
            return False
        if userID == None:
            try:
                account = instagram.get_account(username)
                sleep(1)
                followings = instagram.get_following(account.identifier, maxInList, 100, delayed=True,
                                            maxInList=maxInList)  # Get 150 followers of 'username', 100 a time with random delay between requests
                userID = account.identifier
            except InstagramException as ex:
                if ex.args[0][-3:] == "403":
                    print("User is private. Skipping User")
                else:
                    print("Unknown error")
                    print(ex)
                    sys.exit(1)
            except Exception:
                print("Something went wrong")
        elif username == None:
            try:
                sleep(1)
                followings = instagram.get_following(userID, maxInList, 100, delayed=True,
                                            maxInList=maxInList)
            except InstagramException as ex:
                if ex.args[0][-3:] == "403":
                    print("User is private. Skipping User")
                else:
                    print("Unknown error")
                    print(ex)
                    sys.exit(1)
            except Exception:
                print("Something went wrong")
        try:
            self.createDbEntryFollowers(followings["accounts"])
            self.matchFollowingsToBeingFollowed(userID,followings["accounts"])
            self.setScrapedTrue(userID)
        except Exception as ex:
            print(ex)
            print("Something went wrong")
            print(followings)

    def matchFollowersToBeingFollowed(self,beingFollowedID,FollowerList):  #FollowerID ist Liste
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        #Suchen welchen Key in userData beingFollowedID hat und dann schauen welchen Key FollowerID hat
        beingFollowedKeyQuery = c.execute("""SELECT dbID from userData WHERE instaID = ?""", (beingFollowedID,))

        beingFollowedKey = c.fetchone()[0]
        print(beingFollowedKey)
        for follower in FollowerList:
            instaID = follower.identifier
            followerQuery = c.execute("""SELECT dbID from userData WHERE instaID = ?""", (instaID,))   #extrahiert die Keys der Db
            followerQueryKey = c.fetchone()[0]
            matchingQuery = c.execute("""insert into whoFollowsWho (beingFollowed, follower) values (?,?)""", (beingFollowedKey,followerQueryKey,))
        conn.commit()
        conn.close()

    def matchFollowingsToBeingFollowed(self,FollowingID,beingFollowedList):  #Wem der aktuelle User gerade folgt ist in der Liste
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        #Suchen welchen Key in userData beingFollowedID hat und dann schauen welchen Key FollowerID hat
        followingKeyQuery = c.execute("""SELECT dbID from userData WHERE instaID = ?""", (FollowingID,))
        followingKey = c.fetchone()[0]
        for follower in beingFollowedList:
            instaID = follower.identifier
            beingFollowedQuery = c.execute("""SELECT dbID from userData WHERE instaID = ?""", (instaID,))   #extrahiert die Keys der Db
            beingFollowedKey = c.fetchone()[0]
            matchingQuery = c.execute("""insert into whoFollowsWho (beingFollowed, follower) values (?,?)""",(beingFollowedKey, followingKey,))
        conn.commit()
        conn.close()

    def getMainUserData(self,username): #Wichtig um einen User zu haben der im Mittelpunkt von allem steht
        account = instagram.get_account(username)
        self.createDbEntryFollowers([account]) #Muss liste sein cause of how createDbEntry works
        return account.identifier   #Rückgabe damit man die ID hat um die der anderen fkt zu geben

    def createDbEntryFollowers(self,followersList):  #Soll fungieren als Fkt direkt nachdem die Follower des Main Users extrahiert wurden. Die Daten werden in die Tabelle eingelesen damit sie einen KEy haben und im nächsten Schritt in WhoFollows who eingesetzt werden können
        print("In DB Entry Followers")
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        followersIntoDB = []
        for following in followersList:
            profilPic = following.profile_pic_url
            fullName = following.full_name
            followerID = following.identifier
            followerUsername = following.username
            followerIsPrivate = following.is_private
            infoFollower = (followerID,followerUsername,fullName,profilPic,followerIsPrivate,False,False,False,False)
            print(infoFollower)
            if self.checkIfInDB(followerID) == False:
                print("Wird eingetragen")
                followersIntoDB.append(infoFollower)
        c.executemany('insert into userData (instaID, username, fullName, profilPicUrl, isPrivate, scraped, fromMainUser,picDownload,picNeeded) values (?,?,?,?,?,?,?,?,?)', followersIntoDB)#Speichert jedes Listen element der LISTE followerIntoDB in die Datenbank
        conn.commit()
        conn.close()

    def  checkIfInDB(self,instaID):
        conn = sqlite3.connect(self.dbName)
        print(instaID)
        c = conn.cursor()
        checkSQL = c.execute("""SELECT dbID FROM userData WHERE instaID = ?""", (instaID,))
        checkIfInSQL = c.fetchone()
        conn.close()  # Vielleicht muss hier oben noch ein commit hin NICHT SICHER
        if checkIfInSQL == None:
            return False #Wenn False zurück gegeben wird ist der USER NICHT DRIN
        print("Schon vorhanden in userData")
        return True

    def createDatabase(self):
        dbName = str(int(time.time()))+'.db'
        conn = sqlite3.connect(dbName)
        c = conn.cursor()
        c.execute('''CREATE TABLE userData
                     (dbID INTEGER PRIMARY KEY AUTOINCREMENT,instaID text, username text, fullName text, profilPicUrl text, mediaCount INTEGER, followerCount INTEGER, followingsCount INTEGER, isPrivate BOOLEAN, scraped BOOLEAN, fromMainUser BOOLEAN, picDownload BOOLEAN, picNeeded BOOLEAN)''')  # Noch foreign key und datatypes anpassen
        c.execute('''CREATE TABLE whoFollowsWho
                     (beingFollowed INTEGER, follower INTEGER , FOREIGN KEY(beingFollowed) REFERENCES userData(dbID), FOREIGN KEY(follower) REFERENCES userData(dbID))''')  # Noch foreign key und datatypes anpassen
        conn.commit()
        conn.close()
        self.dbName = dbName
        return dbName

    def startingProcess(self,username,mode=0,maxList=30): #Gathers base data to make further data aggregation possible (based on the given user)
        #Datenbank erstellen
        print("DB erstellt")
        self.createDatabase()
        # Erst eigenen User in die DB eintragen
        print("Main user fetched")
        self.getMainUserData(username=username)
        if mode == 0:
            print("Checking Followers")
            self.listMostRecentFollowers(username=username,maxInList=maxList)
        elif mode == 1:
            print("Checking Followings")
            self.listMostRecentFollowing(username=username,maxInList=maxList)
        else:
            print("Not an available mode!")

    def getAllUsers(self,mode=0,maxList=30):
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        c.execute("""SELECT instaID FROM userData WHERE scraped = False AND fromMainUser = True""")
        notScraped = c.fetchall()
        print(notScraped)
        for userID in notScraped:
            print(userID)
            if mode == 0:
                print("Checking Followers")
                print(userID[0])
                self.listMostRecentFollowers(userID=userID[0],maxInList=maxList)
            elif mode == 1:
                print(userID[0])
                print("Checking Followings")
                self.listMostRecentFollowing(userID=userID[0],maxInList=maxList)
            else:
                print("Not an available mode!")
            sleep(3)
        conn.close()

    def postProcessing(self):
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        c.execute("""UPDATE userData SET fromMainUser = ?""",(True,))
        conn.commit()
        conn.close()


    def fromScratch(self,username,modeMain=0,modeFollowers=0,maxMainUser=30,maxSecondaryUser=30):
        self.login(force=False,two_step_verificator=True)
        sleep(2)
        self.startingProcess(username,modeMain,maxMainUser)
        print("Basics abgeschlossen")
        self.postProcessing()
        self.getAllUsers(modeFollowers,maxSecondaryUser)


    def furtherAggregate(self,dbName,mode=0,maxSecondary=30):
        self.dbName = dbName
        self.getAllUsers(mode,maxSecondary)

    def getPhotoData(self):
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        c.execute("""SELECT dbID,profilPicUrl FROM userData WHERE picDownload = False AND picNeeded = True""")
        profilPicUrls = c.fetchall()
        for picURL in profilPicUrls:
            print(picURL)

            self.downloadProfilePicture(picURL[1],str(picURL[0]))
            c.execute("""UPDATE userData SET picDownload = ? WHERE dbID = ?""",(True,picURL[0],))
            conn.commit()
            rand = random.randint(0,3)
            sleep(rand)
        conn.close()
    def setDbName(self,dbName):
        self.dbName = dbName

    def imageProcessing(self):
        def crop_max_square(pil_img):
            return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

        def crop_center(pil_img, crop_width, crop_height):
            img_width, img_height = pil_img.size
            return pil_img.crop(((img_width - crop_width) // 2,
                                 (img_height - crop_height) // 2,
                                 (img_width + crop_width) // 2,
                                 (img_height + crop_height) // 2))

        def mask_circle_transparent(pil_img, blur_radius, offset=0):
            offset = blur_radius * 2 + offset
            mask = Image.new("L", pil_img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
            result = pil_img.copy()
            result.putalpha(mask)
            return result

        path = os.getcwd()
        print(path)
        fullPath = path + "\\pictures\\"
        liste = os.listdir(fullPath)
        for pic in liste:
            im = Image.open(fullPath + pic)
            # im.thumbnail((150,150))
            # im.save(fullPath+pic.split(".")[0]+'NEWNEW.png', "png")
            im_square = crop_max_square(im).resize((150, 150), Image.LANCZOS)
            im_thumb = mask_circle_transparent(im_square, 4)
            im_thumb.save(fullPath + pic.split(".")[0] + 'Alpha.png')


    def additionalUserInfo(self):   #Only fetches extra info for the people where pictures are required too (not everyone needs
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        c.execute("""SELECT instaID FROM userData WHERE picNeeded = True AND followerCount IS NULL""")  #If followerCount == NUll dann wurde die aktion noch nicht durchgeführt und somit müssen die Daten  noch geholt werden
        profileIDs = c.fetchall()
        additionalInfo = {}
        print(profileIDs)
        for profileID in profileIDs:
            try:
                print(profileID[0])
                account = instagram.get_account_by_id(profileID[0])
                rand = random.randint(0, 3)
                sleep(rand)
                additionalInfo[profileID[0]] = [account.media_count,account.follows_count,account.followed_by_count]
            except Exception:
                print("BROKEN")
                break

        for Info in additionalInfo:
            print(Info)
            c.execute("""UPDATE userData SET mediaCount = ?, followingsCount = ?, followerCount = ? WHERE instaID = ?""", (additionalInfo[Info][0],additionalInfo[Info][1],additionalInfo[Info][2], Info,))

        conn.commit()
        conn.close()

    def ClearFolder(self):
        path = os.getcwd()
        print(path)
        fullPath = path + "\\pictures\\"
        liste = os.listdir(fullPath)
        for pic in liste:
            if pic[-5].isalpha():
                os.remove(fullPath + pic)


instagram = ModifiedInsta()
instagram.with_credentials(MAINUSERNAME, MAINPASSWORD)



#First Parameter MainUser. 2nd Parameter Followers/Followings

instagram.fromScratch("INSTAGRAMUSER",0,1,100,100)#Pass 0 to check most recent followers, pass 1 for most recent followings

##instagram.furtherAggregate("EXISTINGDB.db",0,30)  #Keep collecting data using existing database

#instagram.setDbName("1586871777.db")

dataObject = DataAnalysis(instagram.dbName)

dataObject.networkGraphText(1,1)    #Not all pictures are being downloaded to save time

instagram.getPhotoData()            #downloads profile pictures of needed users


instagram.imageProcessing() #Adds the alpha channel to profile pictures

#Wenn man eine Zahl(Int) übergibt als 2. Parameter werden alle Follower die threshold<=Zahl Connections haben aus dem Graphen geworfen (Standardmäßig 0 damit keiner verloren geht)

dataObject.networkGraph(1,1)# Bei 00, 10 mode=0, Bei 11, 01 mode=1 -> Databasestructure changes based parameters given before the graphing happens
#instagram.additionalUserInfo()  #Gets follower-,follwings- and mediacount for all necessary users


#instagram.ClearFolder()
#! /usr/bin/env python2.6
import MySQLdb
import sqlite3
from my_password import p_mysql

# Our object will handle slave data (s_) and master data (m_)
class MixedDbRecord(object):
	# Init is called only by slave
	def __init__(self,idFile,strFileName,playCount):
		# common for both master & slaver
		self.strFileName = strFileName
		self.totalTimeInSeconds = 0
		
		# slave data
		self.s_idFile = idFile
		self.s_playCount = 0
		# sometime, if playcount is null, we have to force 0 ...
		if(playCount!=None):
			self.s_playCount = playCount
		else:
			self.s_playCount = 0
			
		self.s_idBookmark = 0
		self.s_timeInSeconds = 0
		
		# master data
		self.m_idFile = 0
		self.m_playCount = 0
		self.m_idBookmark = 0
		self.m_timeInSeconds = 0
	
	# Add master data when parsing files database
	def addMysqlFile(self,idFile, playCount):
		self.m_idFile = idFile
		#same issue
		if(playCount!=None):
			self.m_playCount = playCount
		
	# Add slave data when parsing bookmark database
	def addSqliteBookmark(self, idBookmark, timeInSeconds, totalTimeInSeconds):
		if (idBookmark!=None):
			self.s_idBookmark = idBookmark
			self.s_timeInSeconds = timeInSeconds
			self.totalTimeInSeconds = totalTimeInSeconds
			
	# Add master data when parsing bookmark database
	def addMysqlBookmark(self, idBookmark, timeInSeconds, totalTimeInSeconds):
		if (idBookmark!=None):
			self.m_idBookmark = idBookmark
			self.m_timeInSeconds = timeInSeconds
			self.totalTimeInSeconds = totalTimeInSeconds
	
	# Update slave 'files' database
	def updateSqliteFile(self, conn):
		c = conn.cursor()
		sql = "UPDATE files set playCount='%i' where idFile='%i'" % (self.m_playCount, self.s_idFile)
		print "SQLITE : update playcount for %s" %(self.strFileName)
		c.execute(sql)
		conn.commit()

	# Update slave 'bookmark' database	
	def updateSqliteBookmark(self, conn):
		c = conn.cursor()
		sql = "UPDATE bookmark set timeInSeconds='%f' where idFile='%i'" % (self.m_timeInSeconds, self.s_idFile)
		print "SQLITE : update bookmark for %s" %(self.strFileName)
		c.execute(sql)
		conn.commit()
	
	# Insert slave bookmark from master
	def insertSqliteBookmark(self,conn):
		c = conn.cursor()
		# Type is fix to 1 and player to DVDPlayer because that all i need ;)
		sql = "INSERT into bookmark (idFile, timeInSeconds, totalTimeInSeconds, player, type) values (%i, %f,%f,'DVDPlayer',1) " %(self.s_idFile,self.m_timeInSeconds,self.totalTimeInSeconds)
		print "SQLITE : insert bookmark for %s" %(self.strFileName)
		c.execute(sql)
		conn.commit()
		 
	# Update master 'files' database
	def updateMysqlFile(self, conn):
		c = conn.cursor()
		sql = "UPDATE files set playCount='%i' where idFile='%i'" % (self.s_playCount, self.m_idFile)
		print "MYSQL : update playcount for %s" %(self.strFileName)
		c.execute(sql)
		conn.commit()
	
	# Update master 'bookmark' database	
	def updateMysqlBookmark(self, conn):
		c = conn.cursor()
		sql = "UPDATE bookmark set timeInSeconds='%f' where idFile='%i'" % (self.s_timeInSeconds, self.m_idFile)
		print "MYSQL : update bookmark for %s" %(self.strFileName)
		c.execute(sql)
		conn.commit()
		
	# Insert master bookmark from slave
	def insertMysqlBookmark(self,conn):
		c = conn.cursor()
		sql = "INSERT into bookmark (idFile, timeInSeconds, totalTimeInSeconds, player, type) values (%i, %f,%f,'DVDPlayer',1) " %(self.m_idFile,self.s_timeInSeconds,self.totalTimeInSeconds)
		print "MYSQL : insert bookmar for %s" %(self.strFileName)
		c.execute(sql)
		conn.commit()
		
# List of all our records		
dbrecords = []

#-------------------------------------------
# SQLITE : connect
#-------------------------------------------
videodb = "MyVideos34.db"
s_conn = sqlite3.connect('./'+videodb)
s_cursor = s_conn.cursor()

#-------------------------------------------
# SQLITE : populate dbrecords
#-------------------------------------------
s_cursor.execute ("SELECT idFile, strFileName, playCount FROM files")
for row in s_cursor:
	dbrecord = MixedDbRecord(row[0],row[1],row[2])
	dbrecords.append(dbrecord)

#-------------------------------------------
# SQLITE : add bookmark info to the files
#-------------------------------------------
s_cursor.execute ("SELECT idBookmark, idFile, timeInSeconds, totalTimeInSeconds FROM bookmark")
for row in s_cursor:
	for dbsearch in dbrecords:
		if(dbsearch.s_idFile==row[1]):
			dbsearch.addSqliteBookmark(row[0],row[2],row[3])
			break
s_cursor.close()

#-------------------------------------------
# MYSQL : connect
#-------------------------------------------
m_conn = MySQLdb.connect(host = "localhost",
                           user = p_mysql.user,
                           passwd = p_mysql.password,
                           db = "xbmc_video")
m_cursor = m_conn.cursor()

#-------------------------------------------
# MYSQL : add info from 'files' database
#-------------------------------------------
m_cursor.execute ("SELECT idFile, strFileName, playCount FROM files")
for row in m_cursor:
	for dbsearch in dbrecords:
		if(dbsearch.strFileName==row[1]):
			dbsearch.addMysqlFile(row[0],row[2])
			break		

#-------------------------------------------
# SQLITE : add info from bookmark
#-------------------------------------------
m_cursor.execute ("SELECT idBookmark, idFile, timeInSeconds, totalTimeInSeconds FROM bookmark")
for row in m_cursor:
	for dbsearch in dbrecords:
		if(dbsearch.m_idFile==row[1]):
			dbsearch.addMysqlBookmark(row[0],row[2],row[3])
			break

m_cursor.close()


for record in dbrecords:
	# We will apply changes only if we have both idFile from master & slave
	if(record.m_idFile != 0) and (record.s_idFile !=0):
		# Then check the playcount information and update accordingly
		if(record.m_playCount>record.s_playCount):
			record.updateSqliteFile(s_conn)
		elif(record.s_playCount>record.m_playCount):
			record.updateMysqlFile(m_conn)
		
		# For bookmark it's a little bit trickier
		# The bookmark may not be present, so instead of update
		# we will sometime insert !	
		if(record.m_idBookmark != 0):
			if(record.s_idBookmark !=0):
				# both are present : update with the latest one !
				if(record.m_timeInSeconds>record.s_timeInSeconds):
					record.updateSqliteBookmark(s_conn)
				elif(record.s_timeInSeconds>record.m_timeInSeconds):
					record.updateMysqlBookmark(m_conn)
			else:
				# only master bookmark, we will have to insert slave
				record.insertSqliteBookmark(s_conn)
		elif(record.s_idBookmark !=0):
			# only slave bookmark, we will have to insert master
			record.insertMysqlBookmark(m_conn)

# close database connection
s_conn.close()
m_conn.close()


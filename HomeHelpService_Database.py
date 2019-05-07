import mysql.connector
from mysql.connector import Error
import HomeHelpService
import databaseConfig as cfg
import names
import numpy as np
import random

print('run class')

class useDatabase:
    def getDBData():
        print('Connected to Database')
        E = []
        data = {}
        N = []
        locations = {}
        try:
            mySQLconnection  = mysql.connector.connect(**cfg.mysql)
            employees = "select * from Employees"
            patients = "select * from patients"
            cursor = mySQLconnection .cursor()
            
            cursor.execute(employees)
            recordsE = cursor.fetchall()
            for row in recordsE:
                E += [row[0]]
                locations[row[0]]= (row[6], row[7])
                data[row[0]] = row
                jd = {
                    row[0]:{
                    'FirstName': row[1],
                    'LastName': row[2],
                    'Email': row[3],
                    'Phone': row[4],
                    'Address': row[5],
                    'lat': row[6],
                    'long': row[7],
                    'gender': row[8]
                    }
                }
        
            cursor.execute(patients)
            recordsN = cursor.fetchall()
            for row in recordsN:
                N += [row[0]]
                locations[row[0]]= (row[6], row[7])
                data[row[0]] = row
                jd = {
                    row[0]:{
                    'FirstName': row[1],
                    'LastName': row[2],
                    'Email': row[3],
                    'Phone': row[4],
                    'Address': row[5],
                    'lat': row[6],
                    'long': row[7]
                    }
                }
            
            cursor.close()
            mySQLconnection.close()
            return(E, N, locations,data)
        except Error as e :
            print ("Error while connecting to MySQL", e)
            print('Creating random data')
            e = random.randint(5, 10)
            n = random.randint(e,10)
            v = n + e
            N = [i for i in range(n)]
            E = [i for i in range(n, n+e)]  
            loc_xB = np.random.uniform(low=51.4, high=51.5, size=(v))
            loc_yB = np.random.uniform(low=-3.16, high=-3.2, size=(v))
            loc_x =[]
            for num in loc_xB:
                loc_x += [round(num, 6)]
            loc_y =[]
            for num in loc_yB:
                loc_y += [round(num, 6)]
            locations = {}
            for i in range(v):
                locations[i] = (loc_x[i], loc_y[i])
            for i in range(v):
                data[i] = (i, names.get_first_name(), names.get_last_name())
            return(E, N, locations, data)

        
    def runAlgorithm( N, E, locations):
        print('Running algorithm')
        tour = []
        if N != [] and E!=[] and locations!={}:
            HHS = HomeHelpService.mainAlgorithm
            # tour,e,n,relax  = HHS.makeAPIAssignments(N, E, locations) #use this method to make use of the Google Distance API - limit on uses depenting on budget - also needs configuration details
            tour,e,n,relax  = HHS.makeNoAPIAssignments(N, E, locations) #use this method if connection to Google API fails 
            return(tour,e,n,relax)


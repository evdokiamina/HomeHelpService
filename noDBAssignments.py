import mysql.connector
from mysql.connector import Error
import HomeHelpService
import databaseConfig as cfg
import json
import names
import numpy as np

print('run class')

def getDBData():
  print('Creating random data')
  E = []
  data = {}
  N = []
  locations = {}
  n = 10
  e = 5
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
        # tour = HomeHelpService.makeAPIAssignments(N, E, locations)
        tour = HomeHelpService.makeNoAPIAssignments(N, E, locations)
    return tour

E, N, locations, data = getDBData()
tour = runAlgorithm(N, E, locations)
print(locations)
print(tour)
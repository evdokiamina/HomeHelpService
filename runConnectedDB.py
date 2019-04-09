import csv
import HomeHelpService as HHS
import HomeHelpService_Database as DB
import time

with open('testFile_DBAssignments_withConnection.csv', 'w', newline='') as f:
  thewriter = csv.writer(f)

  thewriter.writerow(['execution No.', 'time','tour'])
  for i in range(25):
    start = time.time()
    E, N, locations, data = DB.getDBData()
    tour = DB.runAlgorithm(N, E, locations)
    end = time.time()
    thewriter.writerow([i, (end-start), tour])
f.close()

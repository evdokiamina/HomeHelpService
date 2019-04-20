import csv
import HomeHelpService as HHS
import HomeHelpService_Database as DB
import noDBAssignments as noDB
import time

with open('testFile_RandomAssignmentRandom.csv', 'w', newline='') as f:
  thewriter = csv.writer(f)

  thewriter.writerow(['execution No.', 'time','tour', 'error', 'relax', 'Employee No.', 'Patient No.'])
  for i in range(500):
    start = time.time()
    tour,e,n, relax = HHS.makeRandomAssignments()
    end = time.time()
    errorTour = ''
    if len(tour)!=e:
      errorTour = 'Error'
    thewriter.writerow([i, (end-start), tour, errorTour,relax, e, n])
f.close()

# with open('test_NoConnected.csv', 'w', newline='') as f:
#   thewriter = csv.writer(f)

#   thewriter.writerow(['execution No.', 'time','tour', 'error', 'relax', 'Employee No.', 'Patient No.'])
#   for i in range(100):
#     start = time.time()
#     E, N, locations = DB.getDBData()
#     tour,e,n,relax = DB.runAlgorithm(N, E, locations)
#     end = time.time()
#     print(locations)
#     errorTour = ''
#     if len(tour)!=e:
#       errorTour = 'Error'
#     thewriter.writerow([i, (end-start), tour, errorTour,relax, e, n])
# f.close()

# with open('testFile_NoDBAssignments_noConnection.csv', 'w', newline='') as f:
#   thewriter = csv.writer(f)

#   thewriter.writerow(['execution No.', 'time','tour', 'error'])
#   for i in range(40):
#     start = time.time()
#     E, N, locations, data = noDB.getDBData()
#     tour = noDB.runAlgorithm(N, E, locations)
#     end = time.time()
#     errorTour = ''
#     if len(tour)!=5:
#       errorTour = 'Error'
#     print(locations)
#     thewriter.writerow([i, (end-start), tour, errorTour])
# f.close()
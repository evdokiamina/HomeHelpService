------PROJECT INFORMATION-------
This is my final year Dissertation for my BSc Computer Science degree. 
The aim of the project is to create a solution for the following probelm:
	A Home Help Service company has a number X of employees that need to visit a number Y of elders in their home. We need to find the optimal paths such that 	each employee has an even amount of patients to visit as well as finding the optimal path for them to visit each patient.

-----CODE INFORMATION-----

The HomeHelpService.py file includes 3 versions of the same basic job assignment algorithm:
	- makeRandomAssignments(): completely random, no connections, used to test the main algorithm without delays of generating the interface and attemptng db connections
	- makeAPIAssignments(): once a connection is attempted then this method also tries to connect to the Google API by passing the key to calculate distance
	- makeNoAPIAssignmnets(): if no credit is availabel in the Google API Console, then use this method to calculate distance using the np.hypot() function

The HomeHelpService_Database.py when calling the runAlgorithm() function, if credit available in API console use the makeAPIAssignments() method otherwise comment 
out and use makeNoAPIAssignments() 


-----RUN CODE----------
Ensure you have the following dependecies installed:
	pip install names
	pip install mysql-connector-python
	pip install googlemaps
	pip install matplotlib
	pip install gurobipy
	pip install kivy

To run the code run the following command:
	python HomeHelpService_API.py 


-----TEST CODE-------

To test the code, run the runTests.py file. 
	python runTests.py
Make sure you set the numeber of employees and clients (or the range to randomly generate them) in the HomeHelpService.py file
within the makeRandomAssignments() method as well as the number of times you want to test the algorithm by changing the range
within the runTests.py file 


----MORE INFO---

You can get more infromation by visiting the github repo:
	- https://github.com/evdokiam/HomeHelpService

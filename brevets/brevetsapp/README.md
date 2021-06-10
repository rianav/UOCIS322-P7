##Brevet Time Calculator##

The brevet time calculator takes in control distances in miles or kilometers and returns opening and closing times according to the ACP Brevet Control algorithm. This algorithm follows the ACP minimum and maximum speed table, using the maximum speed to calculate opening times and the minimum speed to calculate closing times.

Example: A control at 890km for a 1000km brevet should have an opening time of 200/34 + 200/32 + 200/30 + 290/28 = 29 hours and 9 minutes. It should have a closing time of 600/15 + 290/11.428 = 65 hours and 23 minutes.

The brevet time calculator includes a Submit and Display button. Clicking submit will allow control times to be inserted into a MongoDB database. Clicking display will display a new page with submitted entries.

Author: Riana Valenzuela 

Email: rianav@uoregon.edu

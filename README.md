# UOCIS322 - Project 7 #
Brevet time calculator.

The brevet time calculator takes in control distances in miles or kilometers and returns opening and closing times according to the ACP Brevet Control algorithm. This algorithm follows the ACP minimum and maximum speed table, using the maximum speed to calculate opening times and the minimum speed to calculate closing times.

Example: A control at 890km for a 1000km brevet should have an opening time of 200/34 + 200/32 + 200/30 + 290/28 = 29 hours and 9 minutes. It should have a closing time of 600/15 + 290/11.428 = 65 hours and 23 minutes.

The brevet time calculator includes a Submit and Display button. Clicking submit will allow control times to be inserted into a MongoDB database. Clicking display will display a new page with submitted entries.

The brevet time calculator includes a consumer program to access brevet time data in csv format, or JSON format with either all data, just open times, or just close times. The user may also specify how many entries they would like to view.

Update: The consumer program to access brevet time data is now password protected. Each user can now register, login, and access data.

Author: Riana Valenzuela Email: rianav@uoregon.edu

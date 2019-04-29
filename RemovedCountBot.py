# ------------------------------------------
# Writtern by u/QuantumBrute
# ------------------------------------------

from psaw import PushshiftAPI
import praw
import sqlite3
import time
import LoginInfoBot

limitno = 30000 # Changes the maximum limit of posts to check

# To change the threshold go to line number 57 and change the number after > sign

print("Starting Bot...")

reddit = praw.Reddit(client_id= LoginInfo.client_id,         
		     client_secret= LoginInfo.client_secret,
		     username= LoginInfo.username,
		     password= LoginInfo.password,
		     user_agent= LoginInfo.user_agent) # Login to reddit API


print("Opening SQL database...")
conn = sqlite3.connect('name_list.db') # Creates a connection object that represents name_list.db
c = conn.cursor()  # Creates a cursor object to perform SQL commands
c.execute('CREATE TABLE IF NOT EXISTS RemovedPostsUsernames(Usernames text)') # DB to store usernames; Creates a table 
conn.commit() # Saves changes to database

api = PushshiftAPI() # Variable to use the PushShiftAPI

end_epoch=int(time.time()) # Current time
start_epoch=int(end_epoch - (60*60*24)) # Current time - the amount you mention in seconds

print("From: "+ str(start_epoch))
print("Till: "+ str(end_epoch))

print("Going through posts...")

def removed():
    result = list(api.search_submissions(after=start_epoch, 
                                        before=end_epoch,
                                        subreddit='ShowerThoughts',
                                        filter=['author','selftext', 'id'],
                                        limit=limitno)) # Gets the data with the parameters mentioned from PushShift and makes it into a list



    numberoftotalposts = len(result) # To store the total number of elements in the list
    print("Total number of posts: " + str(numberoftotalposts))
    a = 0 # To count the number of removed posts; intitalized with 0
    for x in range(numberoftotalposts):
        if reddit.submission(result[x].id).saved:
            continue
        elif result[x].selftext == "[removed]" and result[x].author != "[deleted]": # Checks for removed posts only
            reddit.submission(result[x].id).save()
            c.execute('INSERT INTO RemovedPostsUsernames VALUES (?)', (result[x].author,)) # Inserts the usernames into the table 
            conn.commit() # Dont forget to save!
            a += 1  # +1 to count the number of removed posts everytime it finds a removed post
    print("Total number of removed posts added to database: " + str(a))
    print("Searching for users who exceeded the threshold...")
    for data in c.execute('SELECT Usernames, COUNT(*) FROM RemovedPostsUsernames GROUP BY Usernames HAVING COUNT(*) > 3'): # To check if any user has exceeded the threshold
        print("Threshold exceeded! Sending mail to mods!")
        message = ("u/" + data[0] + " has exceeded the threshold for removed posts with " + str(data[1]) + " posts") # Message to send to modmail
        reddit.subreddit('ShowerThoughts').message('Threshold of removed posts exceeded!', message) # Sends the message to modmail
        print(message)
    conn.close() # Closes the conntection with DB
    print("Operation completed succesfully! You may exit now!")

removed() # To execute the function removed()

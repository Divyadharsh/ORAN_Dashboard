import pandas as pd
import pymongo
import sys
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv


################################## Conneting to MongoDB ############################################# 

#change the details before running or change the uri 
username : "username"
clustername : "clustername"
password: "password"

# MongoDB connection URI
uri = "mongodb+srv://{username}:{password}@{clustername}.8nyt2be.mongodb.net/?retryWrites=true&w=majority"


try:
  client = pymongo.MongoClient(uri)

# return a friendly error if a URI error is thrown 
except pymongo.errors.ConfigurationError:
  print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
  sys.exit(1)

# use a database named "myDatabase"
db = client.myDatabase

################################## Reading and storing the log file in mongoDB   ############################################# 

# Path to your log file
log_file_path = "data/xapp-logger.log"

log_collection = db['log']

# Read the log file and create a list of dictionaries
log_entries = []
with open(log_file_path, "r") as log_file:
    for line in log_file:
        # Assuming each line has the format "timestamp INFO class: message"
        parts = line.strip().split(" ", 3)
        timestamp_str = parts[0] + " " + parts[1]
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
        
        # Calculate Unix epoch timestamp
        unix_epoch_timestamp = int(timestamp.timestamp())
        
        log_entry = {
            "timestamp": timestamp,
            "unix_epoch_timestamp": unix_epoch_timestamp,
            "class": parts[3]
        }
        log_entries.append(log_entry)

# Create a MongoDB document with the name "log_file"
log_document = {
    "_id": "log_file",
    "entries": log_entries
}

# Insert the document into the MongoDB collection
log_collection.insert_one(log_document)

print("Log document inserted successfully.")


################################## Reading the Excelfile  ############################################# 

# use a collection named "csv"
my_collection = db["csv"]


df = pd.read_excel("data/1010123456002_metrics.xlsx")
df["TS"] = (df["Timestamp"] / 1000).apply(lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S:%f')[:-3])


# Iterate over columns and create MongoDB documents
for column_name in df.columns:
    # Skip the "Timestamp" column
    if column_name == "Timestamp":
        continue
# Create a list of dictionaries for the current column
    column_data = []
    for index, row in df.iterrows():
        entry = {
            "unix_epoch": int(row["Timestamp"] / 1000),
            "readable_timestamp": row["TS"],
            "value": row[column_name]
        }
        column_data.append(entry)

    # Create a MongoDB document for the current column
    column_document = {
        "_id": column_name,
        "data": column_data
    }

    # Insert the document into the MongoDB collection
    my_collection.insert_one(column_document)

print("Data inserted successfully.")

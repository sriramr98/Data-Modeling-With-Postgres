# About the Project
We at sparkify have a lot of raw data on user engagement [ wheneve a user takes action ] and we want to analyse the songplay data to run some analytics on it.

Since the data currently is present in flat json files, it's hard to run queries on them. 

The aim of this project is to move the data from json files into an SQL where data analysts can analyse the data further according to their requirements.

# What did we do?
Since we already use postgres at sparkify, I wrote a simple ETL pipeline which moves the data from json files into postgreSQL. 

The amount of data we need to analyze is not big enough to require big data solutions or NoSQL databases.


# Tech Stack
* Python
* Pandas
* PostgreSQL
* Jupyter Notebooks

# Intro to the Datasets

### Songs Dataset
* Data for multiple songs are present in `data/songs_data` folder and is further nested based on the ID.
* For eg, if the `song_id` is `AABC1235ASD235AV`, the json file `AABC1235ASD235AV.json` is present in the path `data/songs_data/A/A/B/AABC1235ASD235AV.json` . 
* The nesting is only upto the first three characters of the ID.
* Each file contains only one json

Sample Record:
```json
{"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, "artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", "song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", "duration": 152.92036, "year": 0}
```

### Logs Dataset
* Each user engagement event is stored as a raw event data in `data/logs_data` folder.
* This folder is further partitioned by `year` and `month` in which the engagement occured.
* Each file contains multiple event json.

Sample Record
```json
{"artist": null, "auth": "Logged In", "firstName": "Walter", "gender": "M", "itemInSession": 0, "lastName": "Frye", "length": null, "level": "free", "location": "San Francisco-Oakland-Hayward, CA", "method": "GET","page": "Home", "registration": 1540919166796.0, "sessionId": 38, "song": null, "status": 200, "ts": 1541105830796, "userAgent": "\"Mozilla\/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/36.0.1985.143 Safari\/537.36\"", "userId": "39"}
```

# Table Schema

![Table Schema](https://i.ibb.co/ChRQpK3/Screenshot-2021-10-25-at-8-40-42-AM.png "Table Schema")

We've desinged a star schema with songplays data as the center [fact table] and artist, song, users and time as dimension tables.

The schema is designed considering the fact that we don't know the query requirements of the Data Analysts other than the fact that they want to analyze songplays.

# How to run the code?

* Install dependencies using `pip3 install -r requirements.txt`
* Setup Postgres Locally
  * A possible method is to use docker. Feel free to choose how you install postgres. We connect to `postgres` user with password `student` so make sure your database also has the same credentials or change it in the code.
  * Download postgres : `docker pull postgres`
  * Create a folder to store postgres data `mkdir -p %{HOME}/postgres-data/`
  * Run postgres: `docker run -d --name dev-postgres -e POSTGRES_PASSWORD=student -v ${HOME}/postgres-data/:/var/lib/postgresql/data -p 5432:5432 postgres`
* Run all cells in `test.ipynb`
import os
import glob
import psycopg2
import pandas as pd
import numpy as np
from io import StringIO
from sql_queries import *

def insert_df_to_postgres(cur, insert_query, df):
    for data in df.values:
        cur.execute(insert_query, data)
        
def run_query(conn, query):
    with conn.cursor() as cur:
        cur.execute(query)
        conn.commit()

def copy(conn, table, df, useIndex=False):
    sio = StringIO()
    
    # Handle NaN
    # Since to_csv writes NaN as empty string, it causes trouble with copy_to since NaN is present in Numeric types
    # So converting NaN in Numeric types to -1
    df = set_empty_defaults_df(df)

    sio.write(df.to_csv(index=useIndex, header=None, sep="|"))
    sio.seek(0)
            
    with conn.cursor() as c:    
        c.copy_from(
            file=sio,
            table=table,
            sep="|"
        )
        conn.commit()
            
def fetch_time_df(df, prop):
    # convert timestamp column to datetime
    t = pd.to_datetime(df[prop], unit='ms')

    column_labels = ('start_time', 'hour', 'day', 'week', 'month', 'year', 'weekday')

    # insert time data records
    time_data = [
        [
            time.value / 1000000,
            int(time.hour),
            int(time.day),
            int(time.week),
            int(time.month),
            int(time.year),
            int(time.dayofweek),
        ]
        for time in t
    ]

    time_df = pd.DataFrame(np.array(time_data), columns=column_labels)

    # all properties are in float, convert to int
    time_df['start_time'] = time_df['start_time'].apply(np.int64)
    time_df['hour'] = time_df['hour'].apply(np.int64)
    time_df['day'] = time_df['day'].apply(np.int64)
    time_df['week'] = time_df['week'].apply(np.int64)
    time_df['month'] = time_df['month'].apply(np.int64)
    time_df['year'] = time_df['year'].apply(np.int64)
    time_df['weekday'] = time_df['weekday'].apply(np.int64)

    return time_df

def process_logs(conn, df):
        
    # filter by NextSong action
    df = df.loc[df['page'] == 'NextSong']
        
    # Fetch timestamp data as DataFrame
    print("Load time data...")
    time_df = fetch_time_df(df, 'ts')
        
    # Insert timestamp data
    print("Insert time data...")
    copy(conn, "time", time_df)
    
    # load user table
    print("Load user data...")
    user_df = df[['userId', 'firstName', 'lastName', 'gender', 'level']]
    user_df['userId'] = user_df['userId'].apply(str)
    
    user_df.drop_duplicates(subset=['userId'], keep='last', inplace=True)
    
    # Insert user data
    print("Insert users data...")
    copy(conn, "users", user_df)
    
    print("Load songplay data..")
    songplay_df = extract_songplays(conn, df)
    
    print("Insert songplat data..")
    copy(conn, "songplays", songplay_df, useIndex=True)


def extract_songplays(conn, df):
    with conn.cursor() as cur:
        songplay_data = []
        # insert songplay records
        for index, row in df.iterrows():

            # get songid and artistid from song and artist tables
            cur.execute(song_select, (row.song, row.artist, row.length))
            results = cur.fetchone()

            songid, artistid = results or (None, None)
            songplay_data.append([row.ts, row.userId, songid, artistid, row.sessionId, row.location, row.userAgent])

        column_labels = ('start_time', 'user_id', 'song_id', 'artist_id', 'session_id', 'location', 'user_agent')
        return pd.DataFrame(np.array(songplay_data), columns=column_labels)

def get_files(filepath):
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))
    
    return all_files
        
    
def process_songs(conn, df):    
    # load songs data
    print("Loading songs...")
    songs_columns = ['song_id', 'title', 'artist_id', 'year', 'duration']
    song_df = df[songs_columns].drop_duplicates(subset=['song_id'], keep='last')
    
    # insert song record
    print("Inserting songs...")
    copy(conn, "songs", song_df)
    
    # load artists data
    print("Loading artists...")
    artist_df = df[['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']].drop_duplicates(subset=['artist_id'], keep='last')
        
    # insert artists data
    print("Inserting artists..")
    copy(conn, "artists", artist_df)
    

def process_data(conn, filepath, func):
    files = get_files(filepath)

    dfs = [pd.read_json(file, lines=True) for file in files]

    df = pd.concat(dfs)

    func(conn, df)
    conn.commit()

    
def set_empty_defaults_df(df):
    for col in df:
        #get type for column
        dt = df[col].dtype
        # if int or float, set -1
        if dt in [int, float]:
            df[col].fillna(-1, inplace=True)

    return df

    
def main():
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=postgres password=student")

    print("Processing song data")
    process_data(conn, filepath='data/song_data', func=process_songs)
    
    print("Processing log data")
    process_data(conn, filepath='data/log_data', func=process_logs)

    print("ETL Completed....")
    conn.close()


if __name__ == "__main__":
    main()
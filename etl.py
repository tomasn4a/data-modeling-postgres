import os
import glob
from typing import Callable

import pandas as pd
import psycopg2
from psycopg2._psycopg import connection, cursor

from sql_queries import *


def process_song_file(cur: cursor, filepath: str) -> None:
    """
    Processes a song file and inserts song and artist records

    Parameters
    ----------
    cur: the database connection cursor
    filepath: the path to a song json file

    """
    # Read song json file into a dataframe
    df = pd.read_json(filepath, lines=True)

    # Prepare and insert song record
    required_cols = ['song_id', 'title', 'artist_id', 'year', 'duration']
    song_data = list(
        df[required_cols].values[0]
    )
    cur.execute(song_table_insert, song_data)
    
    # Prepare and insert artist record
    required_cols = ['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']
    artist_data = list(
        df[required_cols].values[0]
    )
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur: cursor, filepath: str) -> None:
    """
    Process log json file and insert time, user, and songplay records

    Parameters
    ----------
    cur: the database conection cursor
    filepath: the path to the json log file

    """
    # Read json log file to dataframe
    df = pd.read_json(filepath, lines=True)

    # Filter by NextSong action
    df = df[df['page'] == 'NextSong']

    # Convert timestamp column to datetime
    t = pd.to_datetime(df['ts'], unit='ms')
    
    # Prepare and insert time data records
    time_data = [
        s.values for s in (t, t.dt.hour, t.dt.day, t.dt.isocalendar().week, t.dt.month, t.dt.year, t.dt.day_name())
    ]
    column_labels = ('start_time', 'hour', 'day', 'week', 'month', 'year', 'weekday')
    time_df = pd.DataFrame({k: v for k, v in zip(column_labels, time_data)})

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # Load user table
    user_df = df[['userId', 'firstName', 'lastName', 'gender', 'level']]

    # Insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # Prepare and insert songplay records
    for index, row in df.iterrows():
        
        # Get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # Insert songplay record
        songplay_data = (
            pd.to_datetime(row.ts, unit='ms'),
            row.userId,
            row.level,
            songid,
            artistid,
            row.sessionId,
            row.location,
            row.userAgent
        )
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur: cursor, conn: connection, filepath: str, func: Callable) -> None:
    """
    Get all json files in a given directory and apply function

    Parameters
    ----------
    cur: the database connection cursor
    conn: the database connection
    filepath: path to root directory containing json files
    func: the function to apply to each file

    """
    # Get all json files from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # Get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # Iterate over files and apply function
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()
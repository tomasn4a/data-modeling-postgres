# Data Modeling with Postgres

First project for Udacity's Data Engineer Nano-Degree

## Situation

Sparkify, a music streaming company, has some local song
records as well as some history on user activity. The analytics
team wants to understand what songs people are listening to.

Since the song files and user data files currently live in json
files on disk, it is hard to generate this type of insights.

## Task

Our task is to design and implement a relational database
for songs, artist, users, times and songplays, facilitating
the task of the analytics team and ensuring that the data
is accessible and understandable.

## Analysis


We've chosen to follow a star-schema for our database due to 
its simplicity and popularity. The star schema, as its name suggests
consists of a fact table (in our case songplays), linked to multiple
dimension tables (in our case users, songs, artists, and time).

![star_schema](https://upload.wikimedia.org/wikipedia/commons/b/bb/Star-schema.png "Star Schema")

*A Star Schema, source wikimedia*

## Results

By creating the appropriate sql queries for database creation,
destruction, and inserting, along with an ETL pipeline that
processes the json files and performs the inserts we
succesfully moved Sparkify's data from disjoint json files
living on disk to a relational model following a Start schema
and that is ready for analysis.

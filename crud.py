from fastapi import FastAPI
app = FastAPI()

import pymysql
import os

timeout = 10
connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db="defaultdb",
  host="mysql-1003fd63-dbwjdcheld-b2d0.h.aivencloud.com",
  password=os.getenv("AIVEN_PASSWORD"),
  read_timeout=timeout,
  port=11559,
  user="avnadmin",
  write_timeout=timeout,
)
  
@app.get("/articles")
def read_articles():
  try:
      cursor = connection.cursor()
      cursor.execute("SELECT * FROM articles")
      result = cursor.fetchall()
      print(result)
      return result

  finally:
      pass
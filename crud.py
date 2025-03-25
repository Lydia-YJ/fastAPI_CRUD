from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import redis
import pymysql

load_dotenv() 
app = FastAPI()

timeout = int(os.getenv('MYSQL_TIMEOUT'))
connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db=os.getenv('MYSQL_DB'),
  host=os.getenv('MYSQL_HOST'),
  password=os.getenv("AIVEN_PASSWORD"),
  read_timeout=timeout,
  port=int(os.getenv('MYSQL_PORT')),
  user=os.getenv('MYSQL_USER'),
  write_timeout=timeout,)

r = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    decode_responses=True,
    username=os.getenv('REDIS_USER'),
    password=os.getenv('REDIS_PW'))

class Article(BaseModel):
    title: str
    body: str

# success = r.set('foo', 'bar')
# True

# TODO: read from cache (hint) = 캐시(cache)에서 데이터를 읽는 기능을 구현해야 한다
# result = r.get('foo')
# print(result) # >>> bar

@app.post("/articles")
def write_article(article:Article):
    try:
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO articles (title, body) VALUES('{article.title}', '{article.body}')")
    finally:
        pass

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

# 기본 데이터 읽어오기
# @app.get("/articles/{id}")
# def read_articles(id):
#   try:
#       cursor = connection.cursor()
#       cursor.execute(f"SELECT * FROM articles WHERE id={id}")
#       result = cursor.fetchall()[0] #DB API 에서 쿼리 결과를 리스트 형태로 반환
#       print(result)
#       #print(result[-1]) 하나의 데이터를 굳이 리스트로 출력 x
#       return result
#   finally:
#       pass

# 캐시(cache)로 데이터 읽어오기
@app.get("/articles/{id}")
def read_articles(id):
  try:
      cached = r.hgetall(id)
      print('c', cached)
      if cached == {}:
        print("first") # 만약 빈 딕셔너리라면 {} 처음 조회라 데이터가 없다는 뜻
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM articles WHERE id={id}")
        result = cursor.fetchall()[0]
        # print(result['title'], result['body'])
        r.hmset(id, result)
        return result
      else:
         print("cached") # 캐시됨
         return cached
  finally:
      pass
  
@app.put("/articles/{id}")
def update_articles(id, article:Article):
   #DB
   title = article.title
   body = article.body
   try:
      cursor = connection.cursor()
      query = f"UPDATE articles SET title='{article.title}', body='{article.body}' WHERE id={id}"
      cursor.execute(query)
   finally:
      pass
   
   #cache
   r.hmset(id, {'id':id, 'title':title, 'body':body})

@app.delete("/articles/{id}")
def delete_article(id):
    try:
        cursor = connection.cursor()
        query = f"DELETE FROM articles WHERE id={id}"
        cursor.execute(query)
    finally:
        pass

    # Cache
    r.delete(id)

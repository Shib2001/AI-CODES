# Here we are setting up the connection 

from redis import Redis
from rq import Queue

queue = Queue(connection=Redis(
    host="localhost",
    port="6379"
))
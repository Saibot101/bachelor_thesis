import time
from wit import Wit

access_token = "API−Key"

client = Wit(access_token=access_token)
resp = None

t_start = time.time()
try:
  for x in range(70):
  with open( ’examples_english .wav’, ’ rb ’) as f:
  resp = client.speech(f, { ’Content−Type’: ’audio/wav’})
  print( ’response : ’ + str(resp) + ’ ; ’)
  print(resp[" text "])
except:
  print(" error ")

t_end = time.time()
print(t_end - t_start)

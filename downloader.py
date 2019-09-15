import requests
import click
import threading
import pprint
import os
import re

''' 
source code from: https://www.geeksforgeeks.org/simple-multithreaded-download-manager-in-python/
'''

pp = pprint.PrettyPrinter(indent=4)

# The below code is used for each chunk of file handled 
# by each thread for downloading the content from specified  
# location to storage 
def Handler(start, end, url, filename):
  # specify the starting and ending of the file 
  headers = { 'Range': 'bytes=%d-%d' % (start, end)}
  # request the specified part and get into variable 
  r = requests.get(url, headers=headers, stream=True)

  # open the file and write the content of the html page  
  # into file. 
  with open(filename, "r+b") as fp:
    fp.seek(start)
    fp.tell()
    fp.write(r.content)

@click.command(help="It downloads the specified file with specified name") 
@click.option('—number_of_threads',default=4, help="No of Threads") 
@click.option('--name',type=click.Path(),help="Name of the file with extension") 
@click.argument('url_of_file',type=click.Path()) 
@click.pass_context 
def download_file(ctx, url_of_file, name, number_of_threads): 

  if name:
    file_name = name
  else:
    query_pos = url_of_file.find('?')
    if ( query_pos > -1):
      file_name = url_of_file[:query_pos].split('/')[-1]
    else:
      file_name = url_of_file.split('/')[-1]
    
  print(f"start to download {file_name}")

  try:
    r = requests.head(url_of_file)
    file_size = int(r.headers['Content-Length'])
    print(f"file size is : {file_size/1024/1024} M")
  except:
    print('Invalid Url')
    return  
  
  #Create file with size of the content
  part = int(file_size/number_of_threads)
  fp = open(file_name, "wb")
  fp.write(('\0' * file_size).encode())
  fp.close()

  #Now we create Threads and pass the Handler function which has the main functionality :
  for i in range(number_of_threads):
    start = part * i
    end = start + part
    if i == number_of_threads - 1:
      end = file_size
    
    # create a Thread with start and end locations 
    t = threading.Thread(target=Handler, 
      kwargs={'start': start, 'end': end, 'url': url_of_file, 'filename': file_name})
    t.setDaemon(True)
    t.start()
  
  #Finally join the threads and call the “download_file” function from main
  main_thread = threading.current_thread()
  for t in threading.enumerate():
    if t is main_thread:
      continue
    t.join()
  
  print(f'{file_name} downloaded')

if __name__ == '__main__': 
  download_file(obj={}) 
from urllib import parse
from urllib import request
from urllib import response

if __name__ == '__main__':
    url = "http://139.224.128.15:8085/getID"
    response = request.urlopen(url)
    page = response.read()
    print(page)

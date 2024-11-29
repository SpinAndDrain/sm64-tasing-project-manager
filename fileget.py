import requests
from urllib.parse import urlparse


def is_url(s):
    try:
        result = urlparse(s)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


class RemoteFile():
    def __init__(self, url):
        self._url = url
    
    def get_file_info(self):
        try:
            p = urlparse(self._url).path
            p = p[p.rfind("/")+1:]
            i = p.rsplit(".", 1)
            if len(i) != 2:
                i.append(None)
            return i
        except Exception as e:
            print("[Error] While requesting info of remote file: ", e)
            return None, None

    def get_file_size(self):
        try:
            response = requests.head(self._url)
            return int(response.headers.get('Content-Length', -1))
        except Exception as e:
            print("[Error] While requesting size of remote file: ", e)
            return -1
    
    def download(self):
        try:
            response = requests.get(self._url)
            if response.status_code == 200:
                return response.content
            else:
                print(f"[Error] While downloading remote file. status_code={response.status_code}")
                return None
        except Exception as e:
            print("[Error] While downloading remote file: ", e)
            return None

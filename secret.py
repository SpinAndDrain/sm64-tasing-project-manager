import base64
import getpass
import argparse
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random


def read_env_file(path):
    with open(path, "r") as f:
        return read_env(f.read())


def write_env_file(path, env_dict):
    with open(path, "w") as f:
        for k, v in env_dict.items():
            f.write(f"{k}={v}\n")


def read_env(env_str):
    d = {}
    for line in env_str.splitlines():
        name, var = line.partition("=")[::2]
        d[name.strip()] = var
    return d


def encrypt(key, input_path, output_path):
    source = None
    with open(input_path, 'r') as f:
        source = f.read().encode('utf-8')
    key = SHA256.new(key.encode('utf-8')).digest()
    IV = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size
    source += bytes([padding]) * padding
    data = IV + encryptor.encrypt(source)
    with open(output_path, 'wb') as f:
        f.write(data)


def decrypt(key, file_path):
    source = None
    with open(file_path, 'rb') as f:
        source = f.read()
    key = SHA256.new(key.encode('utf-8')).digest()
    IV = source[:AES.block_size]
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])
    padding = data[-1]
    if data[-padding:] != bytes([padding]) * padding:
        print("Invalid padding")
        return None
    return data[:-padding].decode('utf-8')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--path', type=str, required=True)
    parser.add_argument('-k', '--key', type=str)
    parser.add_argument('-o', '--output', type=str)

    args = parser.parse_args()

    key = args.key or getpass.getpass("Encryption password: ")
    outpath = args.output or f"{args.path}.enc"

    try:
        encrypt(key, args.path, outpath)
        print("Encryption successful")
        return
    except FileNotFoundError:
        print(f"File '{file_path}' not found")
    except IOError as e:
        print(f"Error while accessing file '{file_path}': ", e)
    
    print("Encryption failed")


if __name__ == "__main__":
    main()
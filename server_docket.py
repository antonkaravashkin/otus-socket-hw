import socket
from config import LOCALHOST
import datetime
from http import HTTPStatus
import re

http_response = (
    f"HTTP/1.0 200 OK\r\n"
    f"Server: {LOCALHOST}\r\n"
    f"Date: {'%s'%datetime.datetime.now()}\r\n"
    f"Content-Type: text/html; charset=UTF-8\r\n"
    f"\r\n"
)

end_of_stream = '\r\n\r\n'


def status_coder(variable):
    regex = r"^(\S*).(\D*)(\d*)\s([^\\]*)"
    status_code = ""
    if "status" in variable:
        matches = re.finditer(regex, variable, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            for groupNum in range(2, len(match.groups())-1):
                groupNum = groupNum + 1
                status_code = match.group(groupNum)
                if status_code == '':
                    return 200
    elif "status" not in variable:
        return 200
    return status_code.strip()


def client(connection):
    client_data = ""
    new_line = '\n'
    with connection:
        http_status = ""
        while True:
            data = connection.recv(1024)
            if not data:
                break
            client_data += data.decode()
            if end_of_stream in client_data:
                break
        request_type = client_data[:3]
        zeta = client_data.splitlines()
        code = status_coder(zeta[0])
        for i in HTTPStatus:
            if i.value == int(code) and i.value in list(HTTPStatus):
                http_status = (i.value, i.phrase)
                break
            else:
                http_status = (200, 'OK')
        connection.send(http_response.encode()
                        + f"Request Method: {request_type}".encode()
                        + f"\r\n".encode()
                        + f"Request Source: ".encode()
                        + f"{clientAddress}".encode()
                        + f"\r\n".encode()
                        + f"Responce Status: ".encode()
                        + f"{http_status[0]}".encode()
                        + f" {http_status[1]}".encode()
                        + f"\r\n".encode()
                        + f"{new_line.join(zeta[2:])}".encode()
                        + f"\r\n".encode())


with socket.socket() as serversocket:
    serversocket.bind((LOCALHOST, 8086))
    serversocket.listen(5)
    while True:
        (clientConnection, clientAddress) = serversocket.accept()
        client(clientConnection)

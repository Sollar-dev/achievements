# Простой клиент: python client.py 5
import json
import sys
import urllib.error
import urllib.request

URL = "http://localhost:8080/increment"


def send(number):
    body = json.dumps({"number": number}).encode()
    req = urllib.request.Request(URL, data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except ValueError:
            # например 502 от nginx, пока приложение еще не поднялось
            return e.code, raw.decode(errors="replace")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("использование: python client.py <число>")
        sys.exit(1)

    arg = sys.argv[1]
    # если ввели не число, отправляем как строку, пусть сервер сам ругается
    try:
        value = int(arg)
    except ValueError:
        value = arg
    status, data = send(value)
    print(status, data)

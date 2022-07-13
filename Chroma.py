from threading import Thread
from nekoUtils import *
import requests, time
init()

class Driver():
    def __init__(self, device):
        uri, sessionid = self.create()
        self.uri = uri
        self.sessionid = sessionid
        self.device = device
        self.headers = { 'content-type': 'application/json' }
        self.tick = 0
        Thread(target=self.heartbeat, daemon=True).start()


    def __str__(self):
        return f"{MAGENTA}[{WHITE}·{MAGENTA}] SessionID: {WHITE}{self.sessionid}\n{MAGENTA}[{WHITE}·{MAGENTA}] URI: {WHITE}{self.uri}"


    def create(self):
        data = {
            "title": "Neko Razer",
            "description": "Proves xD",
            "author": {
                "name": "Nekoraru22",
                "contact": "https://www.github.com/Nekoraru22"
            },
            "device_supported": ["headset"],
            "category": "application"
        }

        resp = requests.post("http://localhost:54235/razer/chromasdk", json=data, verify=False).json()
        time.sleep(2) # The program needs a little time to connect before change de color XD
        return resp["uri"], resp["sessionid"]


    def remove(self):
        resp = requests.delete(self.uri, verify=False)
        
        if resp.json()["result"] == 0:
            print(f"{RED}[{WHITE}·{RED}] Deleted with " + WHITE + str(self.tick) + RED + " ticks" + RESET)
        else: print(resp.json())


    def heartbeat(self):
        while True:
            try:
                res = requests.put(f"{self.uri}/heartbeat", verify=False)
                time.sleep(1)
                self.tick = res.json()["tick"]
            except: 
                break


    def add(self, ids):
        if len(ids) == 1:
            data = {"id": ids[0]}
        elif len(ids) > 1:
            data = {"ids": ids}
        else: return

        resp = requests.put(f"{self.uri}/effect", json=data)
        errors = []

        try:
            x = 0
            for i in resp.json()["results"]:
                if i["result"] != 0: errors.append(ids[x])
                x += 1
        except: 
            if resp.json()["result"] != 0: errors.append(ids[0])

        if len(errors) > 0: print(Fore.LIGHTRED_EX + "Error on: " + Fore.LIGHTWHITE_EX + ", ".join(errors) + Fore.RESET)
        else: print(Fore.LIGHTGREEN_EX + "[·] Effect aplied: " + Fore.LIGHTWHITE_EX + ", ".join(ids) + Fore.RESET)


    def toBGR(self, hexadecimal):
        x = tuple(hexadecimal[i:i+2] for i in (0, 2, 4))
        decimal = str(x[2]) + str(x[1]) + str(x[0])
        return int(decimal, 16)


    def change(self, hexadecimal):
        color = self.toBGR(hexadecimal)
        
        data = {
            "effect":"CHROMA_CUSTOM",
            "param":[ color, color, color, color ] # Left_Headset, Right_Headset, Left_Kitty, Right_Kitty (BGR format)
        }

        requests.put(f"{self.uri}/{self.device}", json=data, verify=False)

        print(f"{GREEN}[{WHITE}·{GREEN}] Effect aplied on: " + WHITE + f"{self.uri}/{self.device}" + RESET)
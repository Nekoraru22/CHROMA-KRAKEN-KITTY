import requests, time

from threading import Thread
from typing import Tuple
from nekoUtils import *

init()

class Driver():
    def __init__(self, device: str) -> None:
        """Control the color from Razer Chroma
        
        - Krakken kitty ID: devid=FB357780-4617-43A7-960F-D1190ED54806
        """

        uri, sessionid = self.create()
        self.uri = uri
        self.sessionid = sessionid
        self.device = device
        self.headers = { 'content-type': 'application/json' }
        self.tick = 0
        Thread(target=self.heartbeat, daemon=True).start()

    def __str__(self) -> str:
        return f"{MAGENTA}[{WHITE}·{MAGENTA}] SessionID: {WHITE}{self.sessionid}\n{MAGENTA}[{WHITE}·{MAGENTA}] URI: {WHITE}{self.uri}"


    def create(self) -> Tuple[str, int]:
        """Initialize the connection"""

        data = {
            "title": "Neko Chroma",
            "description": "Meow! :3",
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


    def remove(self) -> None:
        """Closes the connection"""

        resp = requests.delete(self.uri, verify=False)
        
        if resp.json()["result"] == 0:
            print(f"{RED}[{WHITE}·{RED}] Deleted with " + WHITE + str(self.tick) + RED + " ticks" + RESET)
        else: print(resp.json())


    def heartbeat(self) -> None:
        """Keeps the connection alive"""

        while True:
            try:
                res = requests.put(f"{self.uri}/heartbeat", verify=False)
                time.sleep(1)
                self.tick = res.json()["tick"]
            except: 
                break


    def add(self, ids: list[int]) -> None:
        """Adds an effect with the assigned IDs"""

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
        else: print(Fore.LIGHTGREEN_EX + "[·] Effect applied: " + Fore.LIGHTWHITE_EX + ", ".join(ids) + Fore.RESET)


    def toBGR(self, hexadecimal: str) -> int:
        """Converts hexadecimal to BGR"""

        x = tuple(hexadecimal[i:i+2] for i in (0, 2, 4))
        decimal = str(x[2]) + str(x[1]) + str(x[0])
        return int(decimal, 16)


    def change(self, data: object, timeout: int, logs: bool) -> None:
        """Applies the received effect"""

        res = requests.put(f"{self.uri}/{self.device}", json=data, verify=False)
        try: print(f"{RED}[{WHITE}·{RED}] {res.json()['error']}{RESET}")
        except: pass

        if logs: print(f"\t{CYAN}↳ {GREEN}Effect applied on: " + WHITE + f"{self.uri}/{self.device}" + RESET)
        
        if timeout > 0: time.sleep(timeout)
        

    # Effects
    def effectNone(self, timeout: int =0, logs: bool =False) -> None:
        """Turn off the colors"""

        data = { "effect": "CHROMA_NONE" }
        self.change(data, timeout, logs)


    def effectStatic(self, hexadecimal: str, timeout: int =0, logs: bool =False) -> None:
        """Adds static color"""

        color = self.toBGR(hexadecimal)

        data = {
            "effect": "CHROMA_STATIC",
            "param": {
                "color": color
            }
        }
        self.change(data, timeout, logs)


    def effectCustom(self, h1: str, h2: str, h3: str, h4: str, timeout: int =0, logs: bool =False) -> None:
        """Adds custom color to Krakken Kitty Headsets
        
        (hexadecimal colors)
        - h1: Left_Headset
        - h2: Right_Headset
        - h3: Left_Kitty
        - h4: Right_Kitty
        """

        c1 = self.toBGR(h1)
        c2 = self.toBGR(h2)
        c3 = self.toBGR(h3)
        c4 = self.toBGR(h4)

        data = {
            "effect":"CHROMA_CUSTOM",
            "param":[ c1, c2, c3, c4 ] # Left_Headset, Right_Headset, Left_Kitty, Right_Kitty (BGR format)
        }
        self.change(data, timeout, logs)
import requests, time, json, urllib3, threading

from prettytable import PrettyTable
from Chroma import Driver
from nekoUtils import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init()

class Partida:
    def __init__(self, ip: str, chroma: Driver =None) -> None:
        """Initialize the game driver on the asigned IP
        Assigning Chroma will also change the colors from the Razer Chroma app."""

        self.url = f"https://{ip}:2999/liveclientdata/allgamedata"
        self.chroma = chroma

        self.firstTime = True
        self.execute = True
        self.inGame = True

        table = PrettyTable([f"{WHITE}Time{RESET}", f"{WHITE}EventType{RESET}", f"{WHITE}Event{RESET}", f"{WHITE}Respawn{RESET}"])
        table.align[f"{WHITE}EventType{RESET}"] = "l"
        table.align[f"{WHITE}Event{RESET}"] = "l"
        table.align[f"{WHITE}Time{RESET}"] = "l"
        self.table = table

        self.ID = 0


    def connet(self) -> None:
        """Starts the connection with the actual game"""

        while self.execute:
            try:
                self.data = requests.get(self.url, verify=False).json()
                self.events = self.data["events"]["Events"]
                new = len(self.events)

                if self.firstTime:
                    self.info()

                    if isinstance(self.colorbase, int): self.chroma.effectStatic(self.colorbase)
                    else: self.chroma.effectCustom(*self.colorbase)
                    
                    self.update()
                    self.firstTime = False

                elif new > self.ID:
                    self.update()
                    self.inGame = True
                
                else: pass
                time.sleep(1)
                    
            except Exception as error:
                if self.inGame: 
                    if not self.firstTime: print("")
                    print(f"{RED}[{WHITE}·{RED}] You are not in game {RESET}")
                    
                    self.inGame = False
                    self.firstTime = True
                    self.ID = 0
                    if not ("Max retries exceeded with url" in str(error) or "Connection aborted" in str(error)):
                        print(f"[·] Error: {error}")
                time.sleep(3)
        
        
    def stop(self) -> None:
        """Stops the connection"""

        self.execute = False
        if self.chroma: self.chroma.remove()


    def time_normalicer(self, seconds: int) -> str:
        """Converts seconds to hour:min:sec"""

        minutes = seconds / 60
        seconds = seconds % 60

        hours = seconds / 60
        minutes = minutes % 60

        def pretty_number(number: int) -> str:
            number = int(number)
            return f'{"0" + str(number) if int(number / 10) == 0 else number}'

        if int(hours) == 0: x = f'{WHITE}{pretty_number(minutes)}{CYAN}:{WHITE}{pretty_number(seconds)}'
        else: x = f'{WHITE}{pretty_number(hours)}{CYAN}:{WHITE}{pretty_number(minutes)}{CYAN}:{WHITE}{pretty_number(seconds)}'

        return x


    def entity_normalicer(self, entity: str, color: bool =True) -> str:
        """Normalice the name and colors for the assigned entity"""

        col = WHITE
        player = False

        chaos_list = ["Minion_T2", "Turret_T2_", "Barracks_T2_"]
        order_list = ["Minion_T1", "Turret_T1_", "Barracks_T1_"]

        def check_order() -> bool:
            x = False
            for i in order_list:
                if str(i) in entity:
                    x = True
                    break
                else: pass
            return x

        def check_chaos() -> bool:
            x = False
            for i in chaos_list:
                if str(i) in entity:
                    x = True
                    break
                else: pass
            return x

        if self.team == "CHAOS":
            if entity in self.team_order: col = RED
            elif entity in self.team_chaos: col = GREEN
            elif check_order(): col = RED
            elif check_chaos(): col = GREEN
            else: pass

        elif self.team == "ORDER":
            if entity in self.team_order: col = GREEN
            elif entity in self.team_chaos: col = RED
            elif check_chaos(): col = RED
            elif check_order(): col = GREEN
            else: pass

        else: pass

        if "Turret_T" in entity: entity = "Turret"
        elif "Minion_T" in entity: entity = "Minion"
        elif "Barracks" in entity: entity = "Barracks"
        elif "SRU_Gromp" in entity: entity = "Gromp"
        elif "SRU_Razorbeak" in entity: entity = "Razorbeak"
        elif "SRU_Red" in entity: entity = "Red_Buff"
        elif "SRU_Blue" in entity: entity = "Blue_Buff"
        elif "SRU_Krug" in entity: entity = "Krug"
        elif "SRU_Murkwol" in entity: entity = "Murkwol"
        elif "TurretShrine_A" in entity: entity = "TurretShrine"
        else: player = True

        if not color: col = WHITE
        if player: return (col + self.all[entity] + BLACK + f"({entity})")
        else: return col + entity


    def connector_normalicer(self, word: str) -> str:
        """Assigns the corresponding connector type"""

        vocals = ["a","e","i","o","u"]
        return f'{"an" if word[0].lower() in vocals else "a"} {BLUE}{word}'


    def getEvent(self) -> None:
        """Filter event types"""

        diff = len(self.events) - self.ID

        for i in range(diff):
            x = self.events[self.ID]
            self.ID += 1

            event = x["EventName"]
            eventID = x["EventID"]


            show = True
            points = True
            resp_time = 0

            if event in ["GameStart", "MinionsSpawning"]:
                temp = f"{YELLOW}UwU{RESET}"
                points = False

            elif event in ["InhibRespawningSoon", "InhibRespawned"]:
                temp = f"{self.entity_normalicer(x[event])}"
                points = False
                
            elif event == "GameEnd":
                temp = f'({RED if x["Result"] == "Lose" else GREEN}{x["Result"]}{CYAN})'

            elif event == "ChampionKill":
                killer = x["KillerName"]
                victim = x["VictimName"]
                
                if self.summonerName == killer:
                    temp = f'{GREEN}You have slain {self.entity_normalicer(victim, False)}'
                    self.colorChange("kill")

                elif self.summonerName == victim:
                    temp = f'{RED}{self.entity_normalicer(killer, False)}{RED} has slain you'
                    resp_time = self.respawn_time()
                    self.colorChange("death", resp_time)

                elif self.summonerName in x["Assisters"]:
                    temp = f'{YELLOW}You assisted {self.entity_normalicer(killer, False)}{YELLOW} to kill {self.entity_normalicer(victim, False)}'

                else:
                    temp = f'{self.entity_normalicer(killer)}{CYAN} has slain {self.entity_normalicer(victim)}'

            elif event == "FirstBlood":
                recipient = x["Recipient"]

                if self.summonerName == recipient:
                    temp = f'{GREEN}You have obtained the first blood'

                else:
                    temp = f'First blood by {self.entity_normalicer(recipient)}{RESET}'

            elif event == "Multikill":
                killer = x["KillerName"]

                if self.summonerName == killer:
                    temp = f'{GREEN}You have a Kill Streak of {BLUE}{x["KillStreak"]}'

                else:
                    temp = f'{self.entity_normalicer(killer)}{CYAN} has a Kill Streak of {BLUE}{x["KillStreak"]}'

            elif event == "TurretKilled":
                killer = x["KillerName"]
                turret = x["TurretKilled"]

                if self.summonerName == killer:
                    temp = f'{GREEN}You have destroyed a {self.entity_normalicer(turret, False)}'
                elif self.summonerName in x["Assisters"]:
                    temp = f'{YELLOW}You assisted {self.entity_normalicer(killer, False)}{YELLOW} to destroy a {self.entity_normalicer(turret, False)}'
                else:
                    temp = f'{self.entity_normalicer(killer)}{CYAN} has destroyed a {self.entity_normalicer(turret, False)}'

            elif event == "InhibKilled":
                killer = x["KillerName"]

                if self.summonerName == killer:
                    temp = f'{GREEN}You have destroyed an inhibitor'
                elif self.summonerName in x["Assisters"]:
                    temp = f'{YELLOW}You assisted {self.entity_normalicer(killer, False)}{YELLOW} to destroy an inhibitor'
                else:
                    temp = f'{self.entity_normalicer(killer)}{CYAN} has destroyed an inhibitor'

            elif event == "Ace":
                acer = x["Acer"]

                if self.summonerName == acer:
                    temp = f'{GREEN}You have done an Ace'
                elif self.team == x["AcingTeam"]:    
                    temp = f'{GREEN}{self.entity_normalicer(acer)}{CYAN} has done an Ace'
                else:
                    temp = f'{RED}{self.all[acer]}{BLACK}({acer}){CYAN} has done an Ace'

            elif event == "FirstBrick":
                killer = x["KillerName"]

                if self.summonerName == killer:
                    temp = f'{GREEN}You have destroyed the first turret'
                else:
                    temp = f'{self.entity_normalicer(killer)}{CYAN} has destroyed the first turret'

            elif event == "DragonKill":
                killer = x["KillerName"]

                if self.summonerName == killer:
                    temp = f'{GREEN}You have killed {self.connector_normalicer(x["DragonType"])} Dragon'
                elif self.summonerName in x["Assisters"] and x["Stolen"]:
                    temp = f'{MAGENTA}You assisted {self.entity_normalicer(killer, False)}{MAGENTA} to steal {self.connector_normalicer(x["DragonType"])} Dragon'
                elif self.summonerName in x["Assisters"] and not x["Stolen"]:
                    temp = f'{YELLOW}You assisted {self.entity_normalicer(killer, False)}{YELLOW} to kill {self.connector_normalicer(x["DragonType"])} Dragon'
                else:
                    temp = f'{self.entity_normalicer(killer)}{CYAN} has killed {self.connector_normalicer(x["DragonType"])} Dragon'
            
            elif event == "HeraldKill":
                killer = x["KillerName"]

                if self.summonerName == killer:
                    temp = f'{GREEN}You have killed the Herald'
                elif self.summonerName in x["Assisters"] and x["Stolen"]:
                    temp = f'{MAGENTA}You assisted {self.entity_normalicer(killer, False)}{MAGENTA} to steal the Herald'
                elif self.summonerName in x["Assisters"] and not x["Stolen"]:
                    temp = f'{YELLOW}You assisted {self.entity_normalicer(killer, False)}{YELLOW} to kill the {MAGENTA}Herald'
                else:
                    temp = f'{self.entity_normalicer(killer)}{CYAN} has killed the {MAGENTA}Herald'

            elif event == "BaronKill":
                killer = x["KillerName"]

                if self.summonerName == killer:
                    temp = f'{GREEN}You have killed the Baron'
                elif self.summonerName in x["Assisters"] and x["Stolen"]:
                    temp = f'{MAGENTA}You assisted {self.entity_normalicer(killer, False)}{MAGENTA} to steal the Baron'
                elif self.summonerName in x["Assisters"] and not x["Stolen"]:
                    temp = f'{YELLOW}You assisted {self.entity_normalicer(killer, False)}{YELLOW} to kill the {MAGENTA}Baron'
                else:
                    temp = f'{self.entity_normalicer(killer)}{CYAN} has killed the {MAGENTA}Baron'

            else: 
                print(x)
                show = False

            # if show: print(f'    {CYAN}[{self.time_normalicer(x["EventTime"])}{CYAN}] {event}{":" if points else ""} {temp}{RESET}') # {eventID} - 
            # if show and resp_time != 0 and len(self.events) == self.ID: print(f'\t\t{WHITE}↳ Respawning in: {BLUE}{resp_time}{RESET}')
            if show:
                if resp_time == 0: resp_time = "-"
                else: resp_time = f"{resp_time} s"
                
                self.table.add_row([f'{CYAN}{self.time_normalicer(x["EventTime"])}{RESET}', f'{CYAN}{event}{RESET}', f'{temp}{RESET}', f'{BLUE}{resp_time}{RESET}'])
                
                if len(self.events) == self.ID: print(self.table)

    def update(self) -> None:
        """Saves the changes in a json"""

        with open("response.json", "w+", encoding="utf-8") as f:
            f.write(json.dumps(self.data, indent=4, sort_keys=True, ensure_ascii=False))
            self.getEvent()


    def skin(self, i: object) -> str:
        """Returns the name of the player's skin if he/she has"""

        try: return f' - {i["skinName"]}'
        except: return ""


    def info(self) -> None:
        """Sorting and storing basic game information such as teams and players"""

        self.summonerName = self.data["activePlayer"]["summonerName"]
        self.gamemode = self.data["gameData"]["gameMode"]
        self.team_order = []
        self.team_chaos = []
        self.all = {}
        self.baseColor()
        
        for i in self.data["allPlayers"]:
            if i["summonerName"] == self.summonerName:
                self.champion = f'{i["championName"]}{self.skin(i)}'
                self.team = i["team"]

            elif i["team"] == "ORDER": self.team_order.append(i["summonerName"])
            elif i["team"] == "CHAOS": self.team_chaos.append(i["summonerName"])

            self.all[i["summonerName"]] = i["championName"]

        print(f'\n{MAGENTA}[{WHITE}·{MAGENTA}] Game Detected\n \
    {CYAN}[{WHITE}·{CYAN}] Summoner Name: {WHITE}{self.summonerName}\n \
    {CYAN}[{WHITE}·{CYAN}] Champion: {WHITE}{self.champion}\n \
    {CYAN}[{WHITE}·{CYAN}] Gamemode: {WHITE}{self.gamemode}\n \
\n{MAGENTA}[{WHITE}·{MAGENTA}] Events \
        ' + RESET)

    
    def respawn_time(self) -> int:
        """Returns the player's respawning time"""

        for i in self.data["allPlayers"]:
            if i["summonerName"] == self.summonerName:
                return round(i["respawnTimer"])
        

    def baseColor(self) -> None:
        """(With Chroma) Sets the default color according to the played map"""

        mapsColors = {"Aram" : "59fafb"}

        if self.gamemode in mapsColors.keys():
            self.colorbase = mapsColors[self.gamemode]
        else: self.colorbase = ["00FFBD", "00FFBD", "1D6E01", "1D6E01"]


    def colorChange(self, event: str, resp_time: int =0) -> None:
        """(With Chroma and Arduino) Change the color according to the type of event"""

        def newThread() -> None:
            if event == "death":
                self.chroma.effectStatic("FF0000", resp_time)
            elif event == "kill":
                self.chroma.effectStatic("00FF00", 3)
            else: return

            if isinstance(self.colorbase, int): self.chroma.effectStatic(self.colorbase)
            else: self.chroma.effectCustom(*self.colorbase)
        
        threading.Thread(target= newThread).start()

# Start #

# game = Partida('127.0.0.1')
# game.connet()
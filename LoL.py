from nekoUtils import *
import requests, time, json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init()

class Partida:
    def __init__(self, chroma=None):
        self.url = "https://127.0.0.1:2999/liveclientdata/allgamedata"
        self.chroma = chroma

        self.firstTime = True
        self.execute = True
        self.inGame = True

        self.ID = 0


    def connet(self):
        while self.execute:
            try:
                self.data = requests.get(self.url, verify=False).json()
                self.events = self.data["events"]["Events"]
                new = len(self.events)

                if self.firstTime:
                    self.info()
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
                    # print(f"[·] Error: {str(error)}")
                time.sleep(3)
        
        
    def stop(self):
        self.execute = False
        if self.chroma: self.chroma.remove()


    def time_normalicer(self, seconds):
        minutes = seconds / 60
        seconds = seconds % 60

        hours = seconds / 60
        minutes = minutes % 60

        def pretty_number(number):
            number = int(number)
            return f'{"0" + str(number) if int(number / 10) == 0 else number}'

        if int(hours) == 0: x = f'{pretty_number(minutes)}:{pretty_number(seconds)}'
        else: x = f'{pretty_number(hours)}:{pretty_number(minutes)}:{pretty_number(seconds)}'

        return x


    def entity_normalicer(self, entity, color=True):
        col = WHITE
        player = False

        chaos_list = ["Minion_T2", "Turret_T2_", "Barracks_T2_"]
        order_list = ["Minion_T1", "Turret_T1_", "Barracks_T1_"]

        def check_order():
            x = False
            for i in order_list:
                if str(i) in entity:
                    x = True
                    break
                else: pass
            return x

        def check_chaos():
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


    def connector_normalicer(self, word):
        vocals = ["a","e","i","o","u"]
        return f'{"an" if word[0].lower() in vocals else "a"} {BLUE}{word}'


    def getEvent(self):
        diff = len(self.events) - self.ID

        for i in range(diff):
            x = self.events[self.ID]
            event = x["EventName"]
            eventID = x["EventID"]
            self.ID += 1
            show = True
            points = True
            resp_time = 0

            if event in ["GameStart", "MinionsSpawning"]:
                temp = ""
                points = False

            elif event in ["InhibRespawningSoon", "InhibRespawned"]:
                self.entity_normalicer(x[event])
                points = False

            elif event == "GameEnd":
                temp = f'({RED if x["Result"] == "Lose" else GREEN}{x["Result"]}{CYAN})'

            elif event == "ChampionKill":
                killer = x["KillerName"]
                victim = x["VictimName"]
                
                if self.summonerName == killer:
                    temp = f'{GREEN}You have slain {self.entity_normalicer(victim, False)}'
                elif self.summonerName == victim:
                    temp = f'{RED}{self.entity_normalicer(killer, False)}{RED} has slain you'
                    resp_time = self.respawn_time()
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

            if show: print(f'    {GREEN}[✔] {CYAN}[{self.time_normalicer(x["EventTime"])}{CYAN}] {event}{":" if points else ""} {temp}{RESET}') # {eventID} - 
            if resp_time != 0: print(f'\t\t↳ Respawning in: {BLUE}{resp_time}{RESET}')

    def update(self):
        with open("response.json", "w+", encoding="utf-8") as f:
            f.write(json.dumps(self.data, indent=4, sort_keys=True))
            self.getEvent()


    def skin(self, i):
        try: return f' - {i["skinName"]}'
        except: return ""


    def info(self):
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


    def baseColor(self):
        mapsColors = {"Aram":0x59fafb}
        if self.gamemode in mapsColors.keys():
            self.color = mapsColors[self.gamemode]
        else: self.color = [0x287E9A, 0x287E9A, 0xA7540F, 0xA7540F]

    
    def respawn_time(self):
        for i in self.data["allPlayers"]:
            if i["summonerName"] == self.summonerName:
                return round(i["respawnTimer"])
        

# Start
game = Partida()
game.connet()
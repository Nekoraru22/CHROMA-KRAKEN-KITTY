from nekoUtils import *
import requests, time, json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Partida:
    def __init__(self, chroma=None):
        self.chroma = chroma

        self.firstTime = True
        self.execute = True
        self.inGame = True

        self.ID = 0

    def connet(self):
        while self.execute:
            try:
                self.data = requests.get("https://127.0.0.1:2999/liveclientdata/allgamedata", verify=False).json()
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
                    print(f"{RED}[{WHITE}·{RED}] You are not in game {RESET}{error}")
                    self.inGame = False
                    self.firstTime = True
                    self.ID = 0
                time.sleep(3)
        
        
    def stop(self):
        self.execute = False
        if self.chroma: self.chroma.remove()
    

    def time_normalice(self, seconds):
        minutes = seconds / 60
        seconds = seconds % 60

        def pretty_number(number):
            return f'{"0" + str(round(number)) if round(number / 10) == 0 else round(number)}'

        return f'{pretty_number(minutes)}:{pretty_number(seconds)}'


    def entity_normalice(self, entity):
        if "Turret" in entity: entity = "Turret"
        elif "Minion" in entity: entity = "Minion"
        
        col = ""

        if self.team == "CHAOS":
            if "T2" in entity: col = GREEN
            elif "T1" in entity: col = RED
        elif self.team == "ORDER":
            if "T2" in entity: col = RED
            elif "T1" in entity: col = GREEN

        return col + entity


    def connector_normalicer(self, word):
        vocals = ["a","e","i","o","u"]
        return f'{"an" if word[0] in vocals else "a"} {word}'


    def team_normalice(self, summoner):
        if self.team == "CHAOS":
            if summoner in self.team_order: col = RED
            elif summoner in self.team_chaos: col = GREEN

        elif self.team == "ORDER":
            if summoner in self.team_order: col = GREEN
            elif summoner in self.team_chaos: col = RED
        
        else: col = WHITE

        return col + summoner

    def getEvent(self):
        diff = len(self.events) - self.ID

        for i in range(diff):
            x = self.events[self.ID]
            event = x["EventName"]
            eventID = x["EventID"]
            self.ID += 1
            show = True
            points = True

            if event in ["GameStart", "MinionsSpawning", "InhibRespawningSoon", "InhibRespawned"]: 
                temp = ""
                points = False

            elif event == "GameEnd":
                temp = f'({RED if x["Result"] == "Lose" else GREEN}{x["Result"]}{CYAN})'

            elif event == "ChampionKill":
                killer = self.entity_normalice(x["KillerName"])
                victim = self.entity_normalice(x["VictimName"])
                
                if self.summonerName == killer:
                    temp = f'{GREEN}You have slain {WHITE}{victim}'
                elif self.summonerName == victim:
                    temp = f'{RED}{WHITE}{killer}{RED} has slain you'
                elif self.summonerName in x["Assisters"]:
                    temp = f'{YELLOW}You assisted {WHITE}{killer}{YELLOW} to kill {WHITE}{victim}'
                else: 
                    temp = f'{WHITE}{killer}{CYAN} has slain {WHITE}{victim}'

            elif event == "FirstBlood":
                recipient = self.entity_normalice(x["Recipient"])

                if self.summonerName == recipient:
                    temp = f'{GREEN}You have obtained the first blood'
                else:
                    temp = f'First blood by {self.team_normalice(recipient)}{RESET}'

            elif event == "Multikill":
                killer = self.entity_normalice(x["KillerName"])

                if self.summonerName == killer:
                    temp = f'{GREEN}You have a Kill Streak of {x["KillStreak"]}'
                else:
                    temp = f'{killer} has a Kill Streak of {x["KillStreak"]}'

            elif event == "TurretKilled":
                killer = self.entity_normalice(x["KillerName"])

                if self.summonerName == killer:
                    temp = f'{GREEN}You have destroyed a {self.entity_normalice(x["TurretKilled"])}'
                elif self.summonerName in x["Assisters"]:
                    temp = f'{YELLOW}You assisted {killer} to destroy a {self.entity_normalice(x["TurretKilled"])}'
                else:
                    temp = f'{WHITE}{killer}{CYAN} has destroyed a {self.entity_normalice(x["TurretKilled"])}'

            elif event == "InhibKilled":
                killer = self.entity_normalice(x["KillerName"])

                if self.summonerName == killer:
                    temp = f'{GREEN}You have destroyed an inhibitor'
                elif self.summonerName in x["Assisters"]:
                    temp = f'{YELLOW}You assisted {killer} to destroy an inhibitor'
                else:
                    temp = f'{WHITE}{killer}{CYAN} has destroyed an inhibitor'

            elif event == "Ace":
                acer = self.entity_normalice(x["Acer"])

                if self.summonerName == acer:
                    temp = f'{GREEN}You have done an Ace'
                elif self.team == x["AcingTeam"] and self.summonerName in x["Assisters"]:
                    temp = f'{YELLOW}You assisted your team to do an Ace ({acer})'
                elif self.team == x["AcingTeam"] and not self.summonerName in x["Assisters"]:    
                    temp = f'{GREEN}{acer}{CYAN} has done an Ace'
                else:
                    temp = f'{RED}{acer}{CYAN} has done an Ace'

            elif event == "FirstBrick":
                killer = self.entity_normalice(x["KillerName"])

                if self.summonerName == killer:
                    temp = f'{GREEN}You have destroyed the first turret'
                else:
                    temp = f'{self.team_normalice(killer)}{CYAN} has destroyed the first turret'

            elif event == "DragonKill":
                killer = self.entity_normalice(x["KillerName"])

                if self.summonerName == killer:
                    temp = f'{GREEN}You have killed {self.connector_normalicer(x["DragonType"])} Dragon'
                elif self.summonerName in x["Assisters"] and x["Stolen"]:
                    temp = f'{MAGENTA}You assisted {WHITE}{killer}{MAGENTA} to steal {self.connector_normalicer(x["DragonType"])} Dragon'
                elif self.summonerName in x["Assisters"] and not x["Stolen"]:
                    temp = f'{YELLOW}You assisted {WHITE}{killer}{YELLOW} to kill {self.connector_normalicer(x["DragonType"])} Dragon'
                else:
                    temp = f'{self.team_normalice(killer)}{CYAN} has killed {self.connector_normalicer(x["DragonType"])} Dragon'
            
            elif event == "HeraldKill":
                killer = self.entity_normalice(x["KillerName"])

                if self.summonerName == killer:
                    temp = f'{GREEN}You have killed the Herald'
                elif self.summonerName in x["Assisters"] and x["Stolen"]:
                    temp = f'{MAGENTA}You assisted {WHITE}{killer}{MAGENTA} to steal an the Herald'
                elif self.summonerName in x["Assisters"] and not x["Stolen"]:
                    temp = f'{YELLOW}You assisted {WHITE}{killer}{YELLOW} to kill the Herald'
                else:
                    temp = f'{self.team_normalice(killer)}{CYAN} has killed the Herald'

            elif event == "BaronKill":
                killer = self.entity_normalice(x["KillerName"])

                if self.summonerName == killer:
                    temp = f'{GREEN}You have killed the Baron'
                elif self.summonerName in x["Assisters"] and x["Stolen"]:
                    temp = f'{MAGENTA}You assisted {WHITE}{killer}{MAGENTA} to steal an the Baron'
                elif self.summonerName in x["Assisters"] and not x["Stolen"]:
                    temp = f'{YELLOW}You assisted {WHITE}{killer}{YELLOW} to kill the Baron'
                else:
                    temp = f'{self.team_normalice(killer)}{CYAN} has killed the Baron'

            else: 
                print(x)
                show = False

            if show: print(f'    {CYAN}[{WHITE}{eventID} - {self.time_normalice(x["EventTime"])}{CYAN}] {event}{":" if points else ""} {temp}{RESET}')

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
        # self.baseColor()
        
        for i in self.data["allPlayers"]:
            if i["summonerName"] == self.summonerName:
                self.champion = f'{i["championName"]}{self.skin(i)}'
                self.team = i["team"]

            elif i["team"] == "ORDER": self.team_order.append(i["summonerName"])
            elif i["team"] == "CHAOS": self.team_chaos.append(i["summonerName"])

        print(f'\n{MAGENTA}[{WHITE}·{MAGENTA}] Game Detected\n \
    {CYAN}[{WHITE}·{CYAN}] Summoner Name: {WHITE}{self.summonerName}\n \
    {CYAN}[{WHITE}·{CYAN}] Champion: {WHITE}{self.champion}\n \
    {CYAN}[{WHITE}·{CYAN}] Gamemode: {WHITE}{self.gamemode}\n \
\n{MAGENTA}[{WHITE}·{MAGENTA}] Events: \
        ' + RESET)


    def baseColor(self):
        mapsColors = {"Aram":"", "Grieta":""}
        self.color = mapsColors[self.gamemode]
        

# Start
game = Partida()
game.connet()
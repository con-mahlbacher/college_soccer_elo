import requests

def sort_helper(team):
    return team.get_elo()

class Wrapper:

    def __init__(self):

        self.teams = []

    def print_rankings(self):
        self.teams.sort(key=sort_helper, reverse=True)
        for i in range(len(self.teams)):
            team = self.teams[i]
            print(str(i+1) + ": " + team.get_name() + "  (" + str(team.get_wins()) + "-" + str(team.get_ties()) + "-" + str(team.get_losses()) + ") " + str(team.get_elo()))

    def get_team(self, team_name):
        for team in self.teams:
            if team.get_name() == team_name:
                return team
        if len(team_name) < 3:
            print()
        new_team = Team()
        new_team.set_name(team_name)
        self.teams.append(new_team)
        return new_team

    def input_match(self, away_team_name, home_team_name, away_score, home_score, neutral):
        away_team = self.get_team(away_team_name)
        home_team = self.get_team(home_team_name)
        result = away_score - home_score
        away_team.add_score(away_score, home_score)
        home_team.add_score(home_score, away_score)
        self.set_elo(away_team, home_team, result, neutral)

    def set_elo(self, away_team, home_team, result, neutral):
        neutral = not neutral
        if result >= 1:
            game_res_1 = 1
            game_res_2 = 0
        elif result == 0:
            game_res_1 = 0.5
            game_res_2 = 0.5
        else:
            game_res_1 = 0
            game_res_2 = 1
            result = result * -1

        k_rate = 50
        if result == 2:
            k_rate = 75
        elif result == 3:
            k_rate = 87.5
        elif result > 3:
            k_rate = 50 + (50 * (3 / 4 + ((result - 3) / 8)))

        diff_rat_1 = away_team.get_elo() - home_team.get_elo() - (100 * neutral)
        diff_rat_2 = home_team.get_elo() - away_team.get_elo() + (100 * neutral)

        expected_res_1 = (1 / (10 ** ((-diff_rat_1) / 400) + 1))
        expected_res_2 = (1 / (10 ** ((-diff_rat_2) / 400) + 1))

        new_elo_1 = away_team.get_elo() + (k_rate * (game_res_1 - expected_res_1))
        new_elo_2 = home_team.get_elo() + (k_rate * (game_res_2 - expected_res_2))

        print(away_team.get_name() + ": " + str(away_team.get_elo()) + " -> " + str(new_elo_1))
        print(home_team.get_name() + ": " + str(home_team.get_elo()) + " -> " + str(new_elo_2))
        print()

        away_team.set_elo(new_elo_1)
        home_team.set_elo(new_elo_2)

class Team:

    def __init__(self):
        self.name = ""
        self.conference = ""
        self.wins = 0
        self.ties = 0
        self.losses = 0
        self.goals = 0
        self.goals_against = 0
        self.elo = 1200

    def get_wins(self):
        return self.wins

    def get_ties(self):
        return self.ties

    def get_losses(self):
        return self.losses

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_elo(self):
        return self.elo

    def set_elo(self, elo):
        self.elo = elo

    def add_score(self, my_score, their_score):
        self.goals += my_score
        self.goals_against += their_score
        if my_score > their_score:
            self.wins += 1
        elif my_score == their_score:
            self.ties += 1
        else:
            self.losses += 1

#List of Non-D1 schools sneaking in
imposters_list = ["Mary Baldwin", "Embry-Riddle (FL)", "", "Assumption", "Webster", "Adrian", "Averett", "Oberlin", "St. Joseph&#39;s (L.I.)", "Suffolk",
                  "Fresno Pacific", "Trinity (TX)", "Aurora", "Blackburn"]

my_wrapper = Wrapper()

#Start of game scraping - 8/24 is first day of season

start_month = 8
start_day = 24

#End of game scraping - Update this with current month/day for up to date rankings
end_month = 10
end_day = 25

while start_month < end_month or start_day < end_day:

    if start_month == 8 and start_day == 32:
        start_month = 9
        start_day = 1
    if start_month == 9 and start_day == 31:
        start_month = 10
        start_day = 1

    month_string = ""
    day_string = ""

    if start_month < 10:
        month_string = "0" + str(start_month)
    else:
        month_string = str(start_month)
    if start_day < 10:
        day_string = "0" + str(start_day)
    else:
        day_string = str(start_day)

    date_string = month_string + "%2F" + day_string + "%2F2023"

    print("---------------- " + month_string + "/" + day_string + "/2023 ---------------------------")


    URL = "https://stats.ncaa.org/season_divisions/18180/livestream_scoreboards?utf8=%E2%9C%93&season_division_id=&game_date=" + date_string + "&conference_id=0&tournament_id=&commit=Submit"
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    }
    page = requests.get(URL, headers=header)
    page_text = page.text

    target_string = "<a target=\"TEAMS_WIN\" class=\"skipMask\" href=\"/teams/556376\"> UAB (0-0-1)</a>"
    target_string_2 = "<a target=\"TEAMS_WIN\" class=\"skipMask\" href=\"/teams/556274\"> Northern Ky. (0-0-1)</a>"
    target_string_3 = "<td rowspan=\"2\" valign=\"center\">"
    target_string_4 = "<td align=\"right\" class=\"totalcol\">"

    #print(len(target_string_4))
    start_index = 0
    end_index = 0

    teams_count = 0
    real_game = True
    neutral_game = False

    away_team_string = ""
    home_team_string = ""
    away_team_name = ""
    home_team_name = ""
    away_score = 0
    home_score = 0

    for i in range(len(page_text)):
        if page_text[i:i+9] == "TEAMS_WIN":
            start_index = i
            while page_text[start_index] != ">":
                start_index += 1
            start_index += 2
            end_index = start_index
            name_end_index = 0
            while page_text[end_index] != "<":
                if page_text[end_index] == "(":
                    name_end_index = end_index - 1
                end_index += 1
            if teams_count % 2 == 0:
                away_team_string = page_text[start_index:end_index]
                away_team_name = page_text[start_index:name_end_index]
                neutral_game = False
                real_game = True
                if away_team_string.__contains__("(0-0)"):
                    real_game = False
                if away_team_name in imposters_list:
                    real_game = False
                if away_team_name == "":
                    print()
            else:
                home_team_string = page_text[start_index:end_index]
                home_team_name = page_text[start_index:name_end_index]
                if home_team_name == "":
                    print()
                if home_team_name in imposters_list:
                    real_game = False
                if home_team_string.__contains__("(0-0)"):
                    real_game = False
                #print("Away: " + away_team_name + " vs. Home: " + home_team_name)
            teams_count += 1
        if page_text[i:i+35] == target_string_4:
            start_index = i+35
            while page_text[start_index] != ">":
                start_index += 1
            start_index += 1
            end_index = start_index
            while page_text[end_index] != "<":
                end_index += 1
            #print("Start " + str(start_index) + "   End " + str(end_index))
            score_string = page_text[start_index:end_index]
            score_int = int(score_string.strip())
            if len(home_team_name) < 2 and len(away_team_name) < 2:
                teams_count += 1
            if teams_count % 2 == 1:
                away_score = score_int
            else:
                home_score = score_int
                if len(away_team_name) < 2 or len(home_team_name) < 2:
                    real_game = False
                print(away_team_name + ": " + str(away_score) + " - " + home_team_name + ": " + str(home_score))
                if real_game:
                    my_wrapper.input_match(away_team_name, home_team_name, away_score, home_score, neutral_game)
                else:
                    print("NOT REAL GAME")
                    print()
                if neutral_game:
                    print("NEUTRAL GAME")
                    print()
                away_team_name = ""
                home_team_name = ""
                away_score = 0
                home_score = 0
            #print(str(teams_count) + " " + score_string.strip())
        if page_text[i:i+32] == "<td rowspan=\"2\" valign=\"center\">":
            if page_text[i+32:i+50].__contains__("@"):
                neutral_game = True
            if page_text[i+32:i+80].__contains__("Canceled"):
                real_game = False
    start_day += 1
my_wrapper.print_rankings()
        #if teams_count % 2 == 0:
            #print(away_team_string + ": " + str(away_score) + " - " + home_team_string + ": " + str(home_score))
                #print(away_team_string + home_team_string + "canceled")

    #print(target_string)
    #print(page.text)
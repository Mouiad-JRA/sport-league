class RankingStrategy:
    def calculate_points(self, game, team):
        raise NotImplementedError

    def calculate_team_points(self, team):
        return sum([self.calculate_points(game, team) for game in team.games])

    def calculate_rankings(self, teams):
        standings = [(team, self.calculate_team_points(team)) for team in teams]
        standings.sort(key=lambda x: (-x[1], x[0].name))
        return standings


class BasicRankingStrategy(RankingStrategy):
    def calculate_points(self, game, team):
        if game.is_draw():
            return 1
        if game.is_winner(team):
            return 3
        return 0


class AlternateRankingStrategy(RankingStrategy):
    def calculate_points(self, game, team):
        if game.is_draw():
            return 1
        if game.is_winner(team):
            return 2
        return 0

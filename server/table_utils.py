from server.server_utils import try_send


def init_client_table(table):
    for player in table.players:
        if not player.bot:
            try_send(player, {"flag": "init_table", "players_data": [
                {"name": gamer.name, "id": gamer.id, "stack": gamer.stack, "is_player": True if gamer == player else False}
                for gamer in table.players]})


def give_players_ids(table):
    i = 0
    for player in table.players:
        player.id = i
        i += 1


def delete(table, player):
    print("ciao ", player.name)
    table.players.remove(player)
    table.nb_players -= 1
    give_players_ids(table)


def add_player(table, player):
    print("hello", player.name, "has joined")
    table.players.append(player)
    player.id = table.nb_players
    table.nb_players += 1
    player.table = table

from websockets.exceptions import ConnectionClosedOK
import cibblbibbl
G = cibblbibbl.CIBBL
G.register_tournaments()
for T in G.tournaments.values():
    for Mu in T.matchups:
        if not Mu.match:
            continue
        Re = Mu.match.replay
        filename = f'{Re.Id:0>8}.json'
        dir_path = "cache/replay"
        p = cibblbibbl.data.path / dir_path / filename
        if not p.is_file():
            print(T)
            print(f'{Mu} {Mu.match.Id} {Re.Id}')
            Re.reload_data()
            if "playerIdnorm" not in Re.config:
                print("generating playerIdnorm values...")
                with Re:
                    Re.playerIdnorm = Re.calculate_playerIdnorm()

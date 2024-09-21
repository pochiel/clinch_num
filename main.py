import csv
import copy
import concurrent.futures
import threading

# 現在の成績表(9/21終了時点)
master_current_status = {
    'G' : [72, 56],
    'T' : [71, 59],
    'B' : [65, 63],
    'C' : [65, 62],
    'Y' : [56, 74],
    'D' : [56, 72],
}

master_remaining_games = [
    {"date": "9-22", "home": "B", "visitor": "Y"},
    {"date": "9-22", "home": "D", "visitor": "C"},
    {"date": "9-22", "home": "T", "visitor": "G"},

    {"date": "9-23", "home": "B", "visitor": "Y"},
    {"date": "9-23", "home": "D", "visitor": "C"},
    {"date": "9-23", "home": "T", "visitor": "G"},

    {"date": "9-25", "home": "B", "visitor": "G"},
    {"date": "9-22", "home": "C", "visitor": "Y"},

    {"date": "9-26", "home": "B", "visitor": "G"},
    {"date": "9-26", "home": "C", "visitor": "Y"},

    {"date": "9-27", "home": "G", "visitor": "D"},
    {"date": "9-27", "home": "C", "visitor": "T"},

    {"date": "9-28", "home": "Y", "visitor": "T"},
    {"date": "9-28", "home": "C", "visitor": "G"},

    {"date": "9-29", "home": "C", "visitor": "D"},
    {"date": "9-29", "home": "T", "visitor": "B"},
    {"date": "9-29", "home": "Y", "visitor": "G"},

    {"date": "9-30", "home": "T", "visitor": "B"},

    {"date": "10-1", "home": "B", "visitor": "C"},

    {"date": "10-2", "home": "B", "visitor": "G"},
    {"date": "10-2", "home": "Y", "visitor": "C"},

    {"date": "10-3", "home": "B", "visitor": "G"},
    {"date": "10-3", "home": "Y", "visitor": "C"},

    {"date": "10-4", "home": "D", "visitor": "B"},

    {"date": "10-5", "home": "D", "visitor": "B"},
    {"date": "10-5", "home": "C", "visitor": "Y"},

    {"date": "10-6", "home": "D", "visitor": "B"},
]

# 勝率の計算
def calculate_win_rate(wins, losses):
    return wins / (wins + losses)

def summary_games(status):
    # チーム成績リストを作成
    team_stats = []
    for team, (wins, losses) in status.items():
        win_rate = calculate_win_rate(wins, losses)
        team_stats.append((team, wins, losses, win_rate))

    # 勝率でソート (降順)
    team_stats.sort(key=lambda x: x[3], reverse=True)

    # 順位付け
    csv_data = []
    for rank, (team, wins, losses, win_rate) in enumerate(team_stats, start=1):
        csv_data.extend([team, wins, losses, f"{win_rate:.3f}", rank])

    # 結果表示用
    #print("CSV出力が完了しました。内容は次の通りです:")
    print(csv_data)
    return csv_data

def simulate_remain_games(remain_games, current_status, csv_data):
    C_WIN_CULUMN = 0
    C_LOSE_CULUMN = 1
    if not remain_games:
        csv_data = csv_data.append(summary_games(current_status))
        return
    else:
        # リストのコピーを作成してpop
        next_remain_games = remain_games.copy()
        current_game = next_remain_games.pop(0)
        # このゲームのホームチームが勝った場合の世界線
        next_current_status = copy.deepcopy(current_status)
        next_current_status[current_game["home"]][C_WIN_CULUMN] = next_current_status[current_game["home"]][C_WIN_CULUMN] + 1
        next_current_status[current_game["visitor"]][C_LOSE_CULUMN] = next_current_status[current_game["visitor"]][C_LOSE_CULUMN] + 1
        simulate_remain_games(next_remain_games, next_current_status, csv_data)

        # このゲームのビジターチームが勝った場合の世界線
        next_current_status = copy.deepcopy(current_status)
        next_current_status[current_game["home"]][C_LOSE_CULUMN] = next_current_status[current_game["home"]][C_LOSE_CULUMN] + 1
        next_current_status[current_game["visitor"]][C_WIN_CULUMN] = next_current_status[current_game["visitor"]][C_WIN_CULUMN] + 1
        simulate_remain_games(next_remain_games, next_current_status, csv_data)

        # 引き分けの場合の世界線
        next_current_status = copy.deepcopy(current_status)
        simulate_remain_games(next_remain_games, next_current_status, csv_data)


# スレッドプールで再帰処理を並列実行する関数
def thread_pool_recursive_function(master_remaining_games, master_current_status, csv_data):
    C_num_threads = 32           # スレッドの数
    # スレッドプールの作成
    with concurrent.futures.ProcessPoolExecutor(max_workers=C_num_threads) as executor:
        # 各スレッドに対して再帰関数を並列に実行
        futures = [executor.submit(simulate_remain_games, master_remaining_games, master_current_status, csv_data)]
        
        # 実行結果を収集
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    return results

# entry point
if __name__ == '__main__':
    csv_data = []
    # スレッドプールで再帰処理を実行
    # results = thread_pool_recursive_function(master_remaining_games, master_current_status, csv_data)
    simulate_remain_games(master_remaining_games, master_current_status, csv_data)
    with open('team_rankings.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)  # 複数行を書き込む


from openai import OpenAI
import openai
import os
import subprocess
import time
import datetime 

# # OpenAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")  # 環境変数から取得
client = OpenAI(api_key=openai.api_key)

# game.pyのパス
GAME_FILE_PATH = "/mnt/c/workspace/OpenCampus/game.py"
LOG_DIR = "/mnt/c/workspace/OpenCampus/log"

def save_backup_code(code: str):
    """
    game.pyの現在のコードをログに保存する。
    """
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(LOG_DIR, f"game_backup_{timestamp}.py")
        with open(log_file_path, "w") as log_file:
            log_file.write(code)
        print(f"バックアップを保存しました: {log_file_path}")
    except Exception as e:
        print(f"バックアップ保存中にエラーが発生しました: {e}")

def read_game_code():
    """
    game.pyのコードを読み取る。
    """
    try:
        with open(GAME_FILE_PATH, "r") as game_file:
            return game_file.read()
    except Exception as e:
        print(f"game.pyの読み取り中にエラーが発生しました: {e}")
        return ""

def modify_game_code(prompt):
    """
    OpenAI APIを使ってgame.pyを変更する。
    """
    try:
        # game.pyの現在のコードを読み取る
        current_code = read_game_code()

        save_backup_code(current_code)

        # OpenAI APIにリクエストを送信
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 使用するモデルを指定
            messages=[
                {"role": "system", "content": "You are a helpful assistant for modifying Python game code."},
                {"role": "user", "content": f"The current game.py code is:\n\n{current_code}\n\nModify it based on the following instruction:\n{prompt}\n\nPlease output only the modified full Python code. Do not include any explanations or comments unless they are part of the code itself."},
                {"role": "assistant", "content": "Sure! Here is the modified code:"}
            ],
            max_tokens=3000,
            temperature=0.7
        )
        # 出力を取得して行に分割
        lines = response.choices[0].message.content.strip().splitlines()

        # 1行目に "python" を含んでいれば削除
        if lines and "```python" in lines[0].lower():
            lines = lines[1:]
        # 最後の行に ``` が含まれる場合、その行を削除
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        new_code = "\n".join(lines)

        # game.pyを更新
        with open(GAME_FILE_PATH, "w") as game_file:
            game_file.write(new_code)


        print("game.pyが更新されました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def restart_game():
    """
    ゲームを再起動する。
    """
    # 現在のゲームプロセスを終了
    subprocess.run(["pkill", "-f", "python.*game.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)  # 少し待機

    # ゲームを再起動
    subprocess.Popen(["python3", GAME_FILE_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("ゲームを再起動しました。")

def main():
    print("ゲームコントローラーが起動しました。")
    print("以下のコマンドを使用できます:")
    print("1. modify: ゲームコードを変更")
    print("2. restart: ゲームを再起動")
    print("3. exit: コントローラーを終了")

    while True:
        command = input("\nコマンドを入力してください: ").strip().lower()

        if command == "modify":
            user_prompt = input("ゲームコードを変更するための指示を入力してください: ")
            modify_game_code(user_prompt)
        elif command == "restart":
            restart_game()
        elif command == "exit":
            print("コントローラーを終了します。")
            break
        else:
            print("無効なコマンドです。")

if __name__ == "__main__":
    main()



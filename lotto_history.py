import json
import os
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

HISTORY_FILE = "lotto_history.json"


def get_latest_draw_no():
    """Fetch the latest draw number from the lottery website."""
    try:
        response = requests.get(
            "https://www.dhlottery.co.kr/gameResult.do?method=byWin",
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException:
        return 0
    soup = BeautifulSoup(response.text, "html.parser")
    draw_no_tag = soup.find("h4")
    if draw_no_tag:
        text = draw_no_tag.get_text()
        digits = "".join(filter(str.isdigit, text))
        if digits:
            return int(digits)
    return 0


def fetch_draw(draw_no):
    """Fetch lotto result for a specific draw number."""
    try:
        resp = requests.get(
            f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}",
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("returnValue") == "success":
            numbers = [
                data.get("drwtNo1"),
                data.get("drwtNo2"),
                data.get("drwtNo3"),
                data.get("drwtNo4"),
                data.get("drwtNo5"),
                data.get("drwtNo6"),
            ]
            return {
                "draw_no": data.get("drwNo"),
                "numbers": numbers,
                "bonus": data.get("bnusNo"),
            }
    except requests.RequestException:
        pass
    return None


def update_lotto_history(file_path=HISTORY_FILE):
    """Update lotto history from latest draw down to 100 draws ago."""
    today = datetime.today().date()
    if os.path.isfile(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                last_update = datetime.fromisoformat(data.get("last_update")).date()
                if last_update == today:
                    return data.get("results", [])
        except Exception:
            pass
    latest_draw_no = get_latest_draw_no()
    if latest_draw_no == 0:
        return []
    results = []
    for draw_no in range(latest_draw_no, latest_draw_no - 100, -1):
        result = fetch_draw(draw_no)
        if result:
            results.append(result)
        time.sleep(0.2)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                {"last_update": today.isoformat(), "results": results},
                f,
                ensure_ascii=False,
                indent=2,
            )
    except Exception:
        pass
    return results


def load_lotto_history(file_path=HISTORY_FILE):
    """Load saved lotto history from file."""
    if os.path.isfile(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("results", [])
        except Exception:
            pass
    return []

from flask import Flask, render_template, jsonify
import random
import time
import json
import os
import datetime
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

TOP_NUMBERS_FILE = 'top_numbers.json'


# Function to generate random lotto numbers
def generate_lotto_numbers():
    # 5개의 번호 조합 생성 
    lotto_numbers = generate_lotto_numbers_all_constraints()
    return lotto_numbers

def generate_lotto_numbers_all_constraints():
    while True:
        numbers = sorted(random.sample(range(1, 46), 6))

        if (
            validate_high_low(numbers) and
            validate_odd_even(numbers) and
            validate_sum_constraint(numbers) and
            validate_end_digit_constraint(numbers) and
            validate_same_range_constraint(numbers) and
            validate_consecutive_constraint(numbers) and
            validate_prime_constraint(numbers) and
            validate_perfect_squares_constraint(numbers) and
            validate_composite_constraint(numbers) and
            validate_end_digit_sum_constraint(numbers) and
            validate_mirror_numbers_constraint(numbers) and
            validate_multiple_of_three_constraint(numbers) and
            validate_multiple_of_four_constraint(numbers) and
            validate_multiple_of_five_constraint(numbers) and
            validate_corner_numbers_constraint(numbers) and
            validate_color_constraint(numbers) and
            validate_double_numbers_constraint(numbers) and
            validate_ac_value_constraint(numbers)
        ):
            return [numbers]  # 1조합만 리스트에 담아 반환

# 각 조건에 대한 유효성 검사 함수
def validate_high_low(numbers):
    low_count = sum(1 for num in numbers if num <= 22)
    high_count = sum(1 for num in numbers if num >= 23)
    return (low_count, high_count) in [(1, 5), (2, 4), (3, 3), (4, 2), (5, 1)]
def validate_odd_even(numbers):
    odd_count = sum(1 for num in numbers if num % 2 != 0)
    even_count = sum(1 for num in numbers if num % 2 == 0)
    return (odd_count, even_count) in [(0, 6), (2, 4), (3, 3), (4, 2), (6, 0)]
def validate_sum_constraint(numbers):
    total_sum = sum(numbers)
    return not (21 <= total_sum <= 80 or 181 <= total_sum <= 260)
def validate_end_digit_constraint(numbers):
    end_digits = [num % 10 for num in numbers]
    digit_counts = {digit: end_digits.count(digit) for digit in set(end_digits)}
    pairs = list(digit_counts.values()).count(2)
    return pairs <= 2
def validate_same_range_constraint(numbers):
    ranges = [((num - 1) // 10) + 1 for num in numbers]
    range_counts = {r: ranges.count(r) for r in set(ranges)}
    return max(range_counts.values()) < 4
def validate_consecutive_constraint(numbers):
    consecutive_count = sum(1 for i in range(len(numbers) - 1) if numbers[i + 1] - numbers[i] == 1)
    return consecutive_count <= 1
def validate_prime_constraint(numbers):
    primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43}
    prime_count = sum(1 for num in numbers if num in primes)
    return 1 <= prime_count <= 3
def validate_perfect_squares_constraint(numbers):
    perfect_squares = {1, 4, 9, 16, 25, 36}
    square_count = sum(1 for num in numbers if num in perfect_squares)
    return 0 <= square_count <= 2
def validate_composite_constraint(numbers):
    composite_numbers = {1, 4, 8, 10, 14, 16, 20, 22, 25, 26, 28, 32, 34, 35, 38, 40, 44}
    composite_count = sum(1 for num in numbers if num in composite_numbers)
    return 1 <= composite_count <= 3
def validate_end_digit_sum_constraint(numbers):
    end_digit_sum = sum(num % 10 for num in numbers)
    return 14 <= end_digit_sum <= 35
def validate_mirror_numbers_constraint(numbers):
    mirror_numbers = {12, 21, 13, 31, 14, 41, 23, 32, 24, 42, 34, 43, 6, 9}
    return not any(num in mirror_numbers for num in numbers)
def validate_multiple_of_three_constraint(numbers):
    multiples_of_three = {3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45}
    multiple_count = sum(1 for num in numbers if num in multiples_of_three)
    return 1 <= multiple_count <= 3
def validate_multiple_of_four_constraint(numbers):
    multiples_of_four = {4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44}
    multiple_count = sum(1 for num in numbers if num in multiples_of_four)
    return 0 <= multiple_count <= 3
def validate_multiple_of_five_constraint(numbers):
    multiples_of_five = {5, 10, 15, 20, 25, 30, 35, 40, 45}
    multiple_count = sum(1 for num in numbers if num in multiples_of_five)
    return 0 <= multiple_count <= 2
def validate_corner_numbers_constraint(numbers):
    corner_numbers = {1, 2, 6, 7, 8, 9, 13, 14, 29, 30, 34, 35, 36, 37, 41, 42}
    corner_count = sum(1 for num in numbers if num in corner_numbers)
    return 1 <= corner_count <= 3
def validate_color_constraint(numbers):
    color_ranges = {
        "yellow": range(1, 11),
        "blue": range(11, 21),
        "red": range(21, 31),
        "gray": range(31, 41),
        "green": range(41, 46)
    }
    colors = set()
    for number in numbers:
        for color, range_values in color_ranges.items():
            if number in range_values:
                colors.add(color)
                break
    return 3 <= len(colors) <= 4
def validate_double_numbers_constraint(numbers):
    double_numbers = {11, 22, 33, 44}
    double_count = sum(1 for num in numbers if num in double_numbers)
    return 0 <= double_count <= 2
def validate_ac_value_constraint(numbers):
    differences = set()
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            differences.add(abs(numbers[i] - numbers[j]))
    ac_value = len(differences)
    return ac_value >= 7

# Function to fetch the latest 5 lotto results
def fetch_latest_lotto_results():
    results = []
    latest_draw_no = get_latest_draw_no()
    if latest_draw_no == 0:  # If we couldn't fetch the latest draw number
        return results
    for draw_no in range(latest_draw_no, latest_draw_no - 5, -1):
        response = requests.get(f'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}')
        if response.status_code == 200:
            data = response.json()
            if data.get('returnValue') == 'success':
                numbers = [
                    data.get('drwtNo1'), data.get('drwtNo2'), data.get('drwtNo3'),
                    data.get('drwtNo4'), data.get('drwtNo5'), data.get('drwtNo6')
                ]
                results.append({
                    'draw_no': data.get('drwNo'),
                    'numbers': numbers,
                    'bonus': data.get('bnusNo')
                })
    return results

def get_latest_draw_no():
    url = 'https://www.dhlottery.co.kr/gameResult.do?method=byWin'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # 최신 회차 번호는 페이지의 특정 위치에 있으므로 해당 요소를 찾아야 합니다.
        # 예를 들어, 회차 번호가 <h4> 태그 내에 있다면:
        draw_no_tag = soup.find('h4')
        if draw_no_tag:
            draw_no_text = draw_no_tag.get_text()
            # '제1157회'와 같은 형식이라면 숫자만 추출
            draw_no = int(''.join(c for c in draw_no_text if c.isdigit()))
            return draw_no
    return 0

def get_ball_style(num):
    if 1 <= num <= 10:
        return "background-color:#fbc400;color:#000;"
    elif 11 <= num <= 20:
        return "background-color:#69c8f2;color:#000;"
    elif 21 <= num <= 30:
        return "background-color:#ff7272;color:#000;"
    elif 31 <= num <= 40:
        return "background-color:#aaa;color:#000;"
    elif 41 <= num <= 45:
        return "background-color:#b0d840;color:#000;"
    return ""

def update_top_frequent_numbers_file():
    latest_draw_no = get_latest_draw_no()
    if latest_draw_no == 0:
        return

    frequency = {}
    for draw_no in range(latest_draw_no, latest_draw_no - 100, -1):
        try:
            response = requests.get(
                f'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}',
                timeout=3
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('returnValue') == 'success':
                    numbers = [
                        data.get('drwtNo1'), data.get('drwtNo2'), data.get('drwtNo3'),
                        data.get('drwtNo4'), data.get('drwtNo5'), data.get('drwtNo6')
                    ]
                    for num in numbers:
                        frequency[num] = frequency.get(num, 0) + 1
            time.sleep(0.1)
        except Exception as e:
            print(f'Error fetching draw {draw_no}: {e}')
            time.sleep(0.5)

    sorted_numbers = sorted(frequency.items(), key=lambda x: (-x[1], x[0]))

    with open(TOP_NUMBERS_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'updated': datetime.datetime.now().isoformat(),
            'top_numbers': sorted_numbers
        }, f, ensure_ascii=False, indent=2)

@app.route('/top-frequent-numbers', methods=['GET'])
def top_frequent_numbers():
    if not os.path.exists(TOP_NUMBERS_FILE):
        update_top_frequent_numbers_file()

    with open(TOP_NUMBERS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 응답 구조 예: {'updated': '2025-06-08T19:30:00', 'top_numbers': [[1, 12], [23, 10], ...]}
    return jsonify(data)

def refresh_top_numbers_if_sunday():
    today = datetime.datetime.today()
    if today.weekday() == 6:  # 일요일 = 6
        print("[일요일] 출현 빈도 갱신 중...")
        update_top_frequent_numbers_file()

def load_top_20_numbers():
    import json
    if not os.path.exists(TOP_NUMBERS_FILE):
        return []

    with open(TOP_NUMBERS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        top_20 = [item[0] for item in data.get('top_numbers', [])[:20]]
        return top_20
    
@app.route('/generate-from-top20', methods=['GET'])
def generate_from_top20():
    top_20 = load_top_20_numbers()
    if len(top_20) < 6:
        return jsonify({'numbers': []})
    numbers = sorted(random.sample(top_20, 6))
    return jsonify({'numbers': numbers})
        
@app.route('/')
def home():
    return render_template(
        'index.html',
        lotto_numbers=generate_lotto_numbers_all_constraints(),
        latest_results=fetch_latest_lotto_results(),
        get_ball_style=get_ball_style,
        top_20_recommend=sorted(random.sample(load_top_20_numbers(), 6))
    )


#새 번호 생성
@app.route('/generate-numbers', methods=['GET'])
def generate_numbers():
    lotto_numbers = generate_lotto_numbers_all_constraints()
    return jsonify({'lotto_numbers': lotto_numbers})

if __name__ == '__main__':
    # 일요일일 경우 캐시 파일 갱신
    import datetime
    if datetime.datetime.today().weekday() == 6:
        update_top_frequent_numbers_file()

    app.run(debug=True)

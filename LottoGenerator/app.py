from flask import Flask, render_template, jsonify
import random
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to generate random lotto numbers
def generate_lotto_numbers():
    # 5개의 번호 조합 생성
    lotto_numbers = generate_lotto_numbers_all_constraints()
    return lotto_numbers

def generate_lotto_numbers_all_constraints():
    results = []

    while len(results) < 5:  # 5개의 로또 번호 조합 생성
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 모든 조건 확인
        if (
                validate_high_low(numbers) and
                validate_odd_even(numbers) and
                validate_same_range_constraint(numbers) and
                validate_consecutive_constraint(numbers) and
                validate_prime_constraint(numbers) and
                validate_perfect_squares_constraint(numbers) and
                validate_composite_constraint(numbers) and
                validate_end_digit_sum_constraint(numbers) and
                validate_multiple_of_three_constraint(numbers) and
                validate_multiple_of_four_constraint(numbers)
        ):
            results.append(numbers)

    return results

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
            draw_no = int(''.join(filter(str.isdigit, draw_no_text)))
            return draw_no
    return 0

@app.route('/')
def home():
    lotto_numbers = generate_lotto_numbers_all_constraints()  # Generate numbers with constraints
    latest_results = fetch_latest_lotto_results()  # Fetch latest lotto results

    # Simulate until match
    # winning_numbers = fetch_latest_lotto()
    # attempts = simulate_lotto_until_match(winning_numbers)
    # last_generated = generate_lotto_numbers_random()

    # num = 0
    # while num < attempts:
    #    last_generated = generate_lotto_numbers_random()

    return render_template(
        'index.html',
        lotto_numbers=lotto_numbers,
        latest_results=latest_results
        # winning_numbers=winning_numbers,
        # attempts=attempts,
        # last_generated=last_generated
    )

#새 번호 생성
@app.route('/generate-numbers', methods=['GET'])
def generate_numbers():
    lotto_numbers = generate_lotto_numbers_all_constraints()
    return jsonify({'lotto_numbers': lotto_numbers})

if __name__ == '__main__':
    app.run(debug=True)


'''
def generate_lotto_numbers_all_constraints_all():
    results = []

    while len(results) < 5:  # 5개의 로또 번호 조합 생성
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 모든 조건 확인
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
            results.append(numbers)

    return results
'''

'''
# 1 고저
def generate_lotto_numbers():
    low_numbers = list(range(1, 23))  # 1~22
    high_numbers = list(range(23, 46))  # 23~45

    # 가능한 패턴 비율 (6:0과 0:6 제거)
    patterns = [
        (1, 5),  # 1 저비율, 5 고비율
        (2, 4),  # 2 저비율, 4 고비율
        (3, 3),  # 3 저비율, 3 고비율
        (4, 2),  # 4 저비율, 2 고비율
        (5, 1)  # 5 저비율, 1 고비율
    ]

    # 랜덤으로 패턴 선택
    pattern = random.choice(patterns)
    low_count, high_count = pattern

    # 패턴에 따라 번호 선택
    selected_low = random.sample(low_numbers, low_count)
    selected_high = random.sample(high_numbers, high_count)

    # 번호를 합치고 정렬
    return sorted(selected_low + selected_high)
# 2 홀짝
def generate_lotto_numbers_with_odd_even():
    numbers = list(range(1, 46))  # 로또 번호 전체
    odd_numbers = [num for num in numbers if num % 2 != 0]  # 홀수 번호
    even_numbers = [num for num in numbers if num % 2 == 0]  # 짝수 번호

    # 가능한 홀짝 패턴 (5:1과 1:5 제외)
    patterns = [
        (0, 6),  # 0 홀수, 6 짝수
        (2, 4),  # 2 홀수, 4 짝수
        (3, 3),  # 3 홀수, 3 짝수
        (4, 2),  # 4 홀수, 2 짝수
        (6, 0)   # 6 홀수, 0 짝수
    ]

    # 랜덤으로 패턴 선택
    pattern = random.choice(patterns)
    odd_count, even_count = pattern

    # 패턴에 따라 번호 선택
    selected_odd = random.sample(odd_numbers, odd_count)
    selected_even = random.sample(even_numbers, even_count)

    # 번호를 합치고 정렬
    return sorted(selected_odd + selected_even)
# 3 총합
def generate_lotto_numbers_with_sum_constraint():
    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 총합 계산
        total_sum = sum(numbers)

        # 제외된 구간 확인 (21~80 및 181~260 제외)
        if not (21 <= total_sum <= 80 or 181 <= total_sum <= 260):
            return numbers
# 4 같은 끝수
def generate_lotto_numbers_with_end_digit_constraint():
    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 끝자리 수 계산
        end_digits = [num % 10 for num in numbers]

        # 끝자리 수의 빈도 계산
        digit_counts = {digit: end_digits.count(digit) for digit in set(end_digits)}

        # 같은 끝수 없음, 2수 1쌍, 2수 2쌍 조건 확인
        pairs = list(digit_counts.values()).count(2)  # '2'는 같은 끝수가 2개인 경우를 의미
        if pairs == 0 or pairs == 1 or pairs == 2:
            return numbers
# 5 동일 구간
def generate_lotto_numbers_with_same_range_constraint():
    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 동일 구간 계산
        ranges = [((num - 1) // 10) + 1 for num in numbers]  # 1~10: 1, 11~20: 2, ..., 41~45: 5
        range_counts = {r: ranges.count(r) for r in set(ranges)}

        # 구간별 숫자의 최대 빈도 확인
        max_count = max(range_counts.values())

        # 동일 구간이 4개 이상인 경우 제외
        if max_count < 4:
            return numbers
# 6 연속번호
def generate_lotto_numbers_with_consecutive_constraint():
    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 연속번호 확인
        consecutive_count = 0
        for i in range(len(numbers) - 1):
            if numbers[i + 1] - numbers[i] == 1:  # 두 숫자가 연속된 경우
                consecutive_count += 1

        # 조건: 연번 없음 또는 2연번(1쌍)만 허용
        if consecutive_count <= 1:  # 연번이 없는 경우(consecutive_count == 0) 또는 1쌍만 허용(consecutive_count == 1)
            return numbers
# 7 소수(1~3개)
def generate_lotto_numbers_with_prime_constraint():
    # 소수 리스트
    primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43}

    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 소수 포함 개수 계산
        prime_count = sum(1 for num in numbers if num in primes)

        # 조건: 소수가 1~3개 포함
        if 1 <= prime_count <= 3:
            return numbers
# 8 완전 제곱수
def generate_lotto_numbers_with_perfect_squares_constraint():
    # 완전제곱수 리스트
    perfect_squares = {1, 4, 9, 16, 25, 36}

    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 완전제곱수 포함 개수 계산
        square_count = sum(1 for num in numbers if num in perfect_squares)

        # 조건: 완전제곱수가 0~2개 포함
        if 0 <= square_count <= 2:
            return numbers
# 9 합성수
def generate_lotto_numbers_with_composite_constraint():
    # 합성수 리스트
    composite_numbers = {1, 4, 8, 10, 14, 16, 20, 22, 25, 26, 28, 32, 34, 35, 38, 40, 44}

    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 합성수 포함 개수 계산
        composite_count = sum(1 for num in numbers if num in composite_numbers)

        # 조건: 합성수가 1~3개 포함
        if 1 <= composite_count <= 3:
            return numbers
# 10 끝수
def generate_lotto_numbers_with_end_digit_sum_constraint():
    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 끝자리 계산 및 총합 구하기
        end_digit_sum = sum(num % 10 for num in numbers)

        # 조건: 끝수 총합이 14~35 사이
        if 14 <= end_digit_sum <= 35:
            return numbers
# 11 동형수
def generate_lotto_numbers_without_mirror_numbers():
    # 동형수 목록
    mirror_numbers = {(12, 21), (13, 31), (14, 41), (23, 32), (24, 42), (34, 43), (6, 9), (9, 6)}
    mirror_set = set(num for pair in mirror_numbers for num in pair)

    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 동형수 존재 여부 확인
        has_mirror = any(num in mirror_set for num in numbers)

        # 조건: 동형수가 없는 경우만 반환
        if not has_mirror:
            return numbers
# 12 3의배수
def generate_lotto_numbers_with_multiple_of_three_constraint():
    # 3의 배수 리스트
    multiples_of_three = {3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45}

    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 3의 배수 포함 개수 계산
        multiple_count = sum(1 for num in numbers if num in multiples_of_three)

        # 조건: 3의 배수가 1~3개 포함
        if 1 <= multiple_count <= 3:
            return numbers
# 13 4의배수
def generate_lotto_numbers_with_multiple_of_four_constraint():
    # 4의 배수 리스트
    multiples_of_four = {4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44}

    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 4의 배수 포함 개수 계산
        multiple_count = sum(1 for num in numbers if num in multiples_of_four)

        # 조건: 4의 배수가 0~3개 포함
        if 0 <= multiple_count <= 3:
            return numbers
# 14 5의배수
def generate_lotto_numbers_with_multiple_of_five_constraint():
    # 5의 배수 리스트
    multiples_of_five = {5, 10, 15, 20, 25, 30, 35, 40, 45}

    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 5의 배수 포함 개수 계산
        multiple_count = sum(1 for num in numbers if num in multiples_of_five)

        # 조건: 5의 배수가 0~2개 포함
        if 0 <= multiple_count <= 2:
            return numbers
# 15 모서리수
def generate_lotto_numbers_with_corner_numbers_constraint():
    # 모서리수 리스트
    corner_numbers = {1, 2, 6, 7, 8, 9, 13, 14, 29, 30, 34, 35, 36, 37, 41, 42}

    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 모서리수 포함 개수 계산
        corner_count = sum(1 for num in numbers if num in corner_numbers)

        # 조건: 모서리수가 1~3개 포함
        if 1 <= corner_count <= 3:
            return numbers
# 16 공색상
def generate_lotto_numbers_with_color_constraint():
    # 색상 범위 정의
    color_ranges = {
        "yellow": range(1, 11),  # 1~10
        "blue": range(11, 21),  # 11~20
        "red": range(21, 31),  # 21~30
        "gray": range(31, 41),  # 31~40
        "green": range(41, 46)  # 41~45
    }

    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 번호의 색상 분포 계산
        colors = set()
        for number in numbers:
            for color, range_values in color_ranges.items():
                if number in range_values:
                    colors.add(color)
                    break

        # 조건: 색상 개수가 3~4개만 포함
        if 3 <= len(colors) <= 4:
            return numbers
# 17 쌍수
def generate_lotto_numbers_with_double_numbers_constraint():
    # 쌍수 리스트
    double_numbers = {11, 22, 33, 44}

    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # 쌍수 포함 개수 계산
        double_count = sum(1 for num in numbers if num in double_numbers)

        # 조건: 쌍수가 0~2개 포함
        if 0 <= double_count <= 2:
            return numbers
# 18 AC값
def calculate_ac_value(numbers):
    """AC 값을 계산하는 함수"""
    differences = set()
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            differences.add(abs(numbers[i] - numbers[j]))
    return len(differences)
def generate_lotto_numbers_with_ac_value_constraint():
    while True:
        # 번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))

        # AC 값 계산
        ac_value = calculate_ac_value(numbers)

        # 조건: AC 값이 7 이상
        if ac_value >= 7:
            return numbers
'''

'''
# 최신 회차에서 몇번을 돌려 1등이 나오는지 확인 후 횟수대로 돌리기
def fetch_latest_lotto():
    response = requests.get('https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo=1151')
    if response.status_code == 200:
        data = response.json()
        if data.get('returnValue') == 'success':
            return sorted([
                data.get('drwtNo1'), data.get('drwtNo2'), data.get('drwtNo3'),
                data.get('drwtNo4'), data.get('drwtNo5'), data.get('drwtNo6')
            ])
    return []
def generate_lotto_numbers_random():
    return sorted(random.sample(range(1, 46), 6))
def simulate_lotto_until_match(winning_numbers):
    attempts = 0
    while True:
        attempts += 1
        generated_numbers = generate_lotto_numbers_random()
        if generated_numbers == winning_numbers:
            return attempts
'''
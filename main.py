import time
import json

EPSILON = 1e-9

# ==================== 기능 관련 ====================
def measure_time(pattern, filter, repeat=10):
    start = time.perf_counter()
    for _ in range(repeat):
        mac_operation(pattern, filter)
    end = time.perf_counter()
    return (end - start) * 1000 / repeat  # ms


def mac_operation(pattern, filter):
    total = 0.0
    n = len(pattern)
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filter[i][j]
    return total


# ==================== 모드 1 ====================
def mode_user_input():
    print("---------------------------------")
    print("[1] 필터 입력")
    print("---------------------------------")
    A = input_matrix(3, "필터 A")
    B = input_matrix(3, "필터 B")

    print("---------------------------------")
    print("[2] 패턴 입력")
    print("---------------------------------")
    P = input_matrix(3, "패턴")

    score_a = mac_operation(P, A)
    score_b = mac_operation(P, B)
    avg_time = (measure_time(P, A) + measure_time(P, B)) / 2

    result = compare_scores_mode1(score_a, score_b)

    print("---------------------------------")
    print("[3] MAC 결과")
    print("---------------------------------")
    print(f"A 점수 : {score_a}")
    print(f"B 점수 : {score_b}")
    print(f"연산 시간(평균/10회) : {avg_time:.6f} ms")

    if result == "UNDECIDED":
        print("판정 : 판정 불가(|A-B| < 1e-9)\n")
    else:
        print(f"판정 : {result}\n")


def compare_scores_mode1(a, b):
    # A vs B
    if abs(a - b) < EPSILON:
        return "UNDECIDED"
    return "A" if a > b else "B"


def input_matrix(n, name):
    print(f"{name} ({n}줄 입력, 공백 구분)")
    matrix = []
    while True:
        matrix.clear()
        try:
            for _ in range(n):
                row = list(map(float, input().split()))
                if len(row) != n:
                    raise ValueError
                matrix.append(row)
            print()
            return matrix
        except:
            print("입력 형식 오류 : 각 줄에 {}개의 숫자를 공백으로 구분해 입력하세요.".format(n))


# ==================== 모드 2 ====================
def mode_json():
    try:
        data = load_json()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[오류] {e}")
        print("프로그램을 종료합니다.\n")
        return

    print("---------------------------------")
    print("[1] 필터 로드")
    print("---------------------------------")

    filters = {}
    for key, value in data["filters"].items():
        size = int(key.split("_")[1])

        filters[size] = {}
        for fkey, fval in value.items():
            filters[size][normalize_label(fkey)] = fval

        print(f"{key} 필터 로드 완료 (Cross, X)\n")

    print("---------------------------------")
    print("[2] 패턴 분석 (라벨 정규화 적용)")
    print("---------------------------------")

    total = 0
    passed = 0
    failed_cases = []

    for key, value in data["patterns"].items():
        print(f"— {key} —")
        total += 1

        try:
            parts = key.split("_")
            size = int(parts[1])

            pattern = value["input"]
            expected = normalize_label(value["expected"])

            if size not in filters:
                raise Exception("필터 없음")

            f_cross = filters[size]["Cross"]
            f_x = filters[size]["X"]

            if not validate_size(pattern, f_cross):
                raise Exception("행/열 수 불일치")

            score_cross = mac_operation(pattern, f_cross)
            score_x = mac_operation(pattern, f_x)

            result = compare_scores_mode2(score_cross, score_x)
            if result == "UNDECIDED":
                raise Exception("동점 규칙")

            is_pass = (result == expected)

            print(f"Cross 점수 : {score_cross}")
            print(f"X 점수 : {score_x}")
            print(f"판정 : {result} | expected: {expected} | {'PASS' if is_pass else 'FAIL'}\n")

            if is_pass:
                passed += 1
            else:
                raise Exception("기대값 불일치")

        except Exception as e:
            print(f"FAIL ({str(e)})\n")
            failed_cases.append((key, str(e)))


def load_json():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)
    

# 라벨 정규화 
def normalize_label(label: str) -> str:
    label = label.lower()
    if label in ["+", "cross"]:
        return "Cross"
    elif label in ["x"]:
        return "X"
    return "UNKNOWN"


def validate_size(pattern, filter):
    return len(pattern) == len(filter) and len(pattern[0]) == len(filter[0])


def compare_scores_mode2(cross_score, x_score):
    # Cross vs X
    if abs(cross_score - x_score) < EPSILON:
        return "UNDECIDED"
    return "Cross" if cross_score > x_score else "X"
    

# ==================== 메인 ====================
def main():
    print("=== Mini NPU Simulator ===")
    print("\n[모드 선택]\n")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")

    choice = input("선택 : ")
    print()

    if choice == "1":
        mode_user_input()
    elif choice == "2":
        mode_json()
    else:
        print("잘못된 입력입니다.")


if __name__ == "__main__":
    main()
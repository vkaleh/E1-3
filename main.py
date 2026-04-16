import time
import json

EPSILON = 1e-9

# ==================== 기능 관련 ====================
def measure_time(func, pattern, filter, repeat=10):
    start = time.perf_counter()
    for _ in range(repeat):
        func(pattern, filter)
    end = time.perf_counter()
    return (end - start) * 1000 / repeat    # ms 


def mac_operation_2d(pattern, filter):
    total = 0.0
    n = len(pattern)
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filter[i][j]
    return total


def mac_operation_1d(pattern_1d, filter_1d):
    total = 0.0
    size = len(pattern_1d)
    for i in range(size):
        total += pattern_1d[i] * filter_1d[i]
    return total


# 2D -> 1D 변환 함수
def flatten(matrix):
    flat = []
    for row in matrix:
        for val in row:
            flat.append(val)
    return flat


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

    score_a = mac_operation_2d(P, A)
    score_b = mac_operation_2d(P, B)
    avg_time = (measure_time(mac_operation_2d, P, A) + measure_time(mac_operation_2d, P, B)) / 2

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

        is_pass = False
        fail_reason = ""

        try:
            parts = key.split("_")
            size = int(parts[1])
            pattern = value["input"]
            expected = normalize_label(value["expected"])

            if size not in filters:
                fail_reason = "필터 없음"

            f_cross = filters[size]["Cross"]
            f_x = filters[size]["X"]

            if size not in filters:
                fail_reason = "행/열 수 불일치"

            score_cross = mac_operation_2d(pattern, f_cross)
            score_x = mac_operation_2d(pattern, f_x)

            result = compare_scores_mode2(score_cross, score_x)
            if result == "UNDECIDED":
                fail_reason = "동점 규칙"
            elif result == expected:
                is_pass = True
                passed += 1
            else:
                fail_reason = "기대값 불일치"

        except Exception as e:
            fail_reason = f"{e}"

        # 성공/실패 여부와 관계없이 계산된 값들을 모두 출력
        print(f"Cross 점수 : {score_cross}")
        print(f"X 점수 : {score_x}")

        if not is_pass:
            print(f"판정 : {result} | expected: {expected} | FAIL ({fail_reason})\n")
            failed_cases.append((key, fail_reason))
        else:
            print(f"판정 : {result} | expected: {expected} | PASS\n")
            
    print("---------------------------------")
    print("[3] 성능 분석 (평균/10회)")
    print("---------------------------------")
    print("크기\t2D 평균 시간\t1D 평균 시간\t연산 횟수")

    # size별 시간 누적용
    perf_data = {
        # size: { "2d": [...], "1d": [...] }
    }

    # 3x3 성능 측정
    size = 3
    pattern3x3 = [[1.0]*size for _ in range(size)]
    filter3x3 = [[1.0]*size for _ in range(size)]

    pattern3x3_1d = flatten(pattern3x3)
    filter3x3_1d = flatten(filter3x3)

    if size not in perf_data:
        perf_data[size] = {"2d": [], "1d": []}

    avg_time_2d = measure_time(mac_operation_2d, pattern3x3, filter3x3)
    avg_time_1d = measure_time(mac_operation_1d, pattern3x3_1d, filter3x3_1d)
    
    perf_data[size]["2d"].append(avg_time_2d)
    perf_data[size]["1d"].append(avg_time_1d)

    # 5x5, 13x13, 25x25 성능 측정 
    for key, value in data["patterns"].items():
        try:
            parts = key.split("_")      # size_5_1 -> [size, 5, 1]
            size = int(parts[1])

            pattern = value["input"]
            pattern_1d = flatten(pattern)

            # 해당되는 사이즈의 필터가 없으면 넘어감 
            if size not in filters:
                continue

            crossFilter = filters[size]["Cross"]
            xFilter = filters[size]["X"]

            crossFilter_1d = flatten(crossFilter)
            xFilter_1d = flatten(xFilter)

            if not validate_size(pattern, crossFilter) or not validate_size(pattern, xFilter):
                continue

            # 시간 측정
            avg_time_cross_2d = measure_time(mac_operation_2d, pattern, crossFilter)
            avg_time_x_2d = measure_time(mac_operation_2d, pattern, xFilter)
            avg_time_2d = (avg_time_cross_2d + avg_time_x_2d) / 2

            avg_time_cross_1d = measure_time(mac_operation_1d, pattern_1d, crossFilter_1d)
            avg_time_x_1d = measure_time(mac_operation_1d, pattern_1d, xFilter_1d)
            avg_time_1d = (avg_time_cross_1d + avg_time_x_1d) / 2

            if size not in perf_data:
                perf_data[size] = {"2d": [], "1d": []}

            perf_data[size]["2d"].append(avg_time_2d)
            perf_data[size]["1d"].append(avg_time_1d)

        except:
            continue

    # 결과 출력 (size별 평균)
    for size in sorted(perf_data.keys()):
        times_2d = perf_data[size]["2d"]
        times_1d = perf_data[size]["1d"]

        avg_2d = sum(times_2d) / len(times_2d)
        avg_1d = sum(times_1d) / len(times_1d)

        print(f"{size}x{size}\t{avg_2d:.6f}\t{avg_1d:.6f}\t{size*size}")

    print("\n---------------------------------")
    print("[4] 결과 요약")
    print("---------------------------------")
    print(f"총 테스트 : {total}개")
    print(f"통과 : {passed}개")
    print(f"실패 : {total - passed}개")

    if failed_cases:
        print("\n실패 케이스:")
        for case, reason in failed_cases:
            print(f"- {case} : {reason}")


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
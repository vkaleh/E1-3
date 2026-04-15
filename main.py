import time

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


# ==================== 입력 처리 ====================
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
        print("data.json 분석 모드")
    else:
        print("잘못된 입력입니다.")


if __name__ == "__main__":
    main()
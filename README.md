# Mini NPU Simulator 개발

## 1. 프로젝트 개요
MAC 연산을 구현하여 패턴과 필터 간 유사도를 계산하고, 3x3부터 25x25까지 다양한 크기의 데이터를 판별하는 mini NPU 시뮬레이터를 개발하는 프로젝트이다. <br>
데이터 크기에 따라 연산 시간이 어떻게 변하는지 직접 계산해보고, 구현 과정에서 발생하는 문제를 해결해본다. 
<p align="center">&nbsp;</p>

## 2. 실행 방법
Python version : 3.12.13

```bash
% git clone ....git
% cd E1-3
% python main.py
```

<br>

**파일 구조**
```bash
E1-3
├── main.py              
├── data.json            # 패턴, 필터 데이터 
└── README.md
```

<br>

**모드 선택 방법**
프로그램 실행 후 모드를 선택한다.

1번 (사용자 입력 모드)
- 3x3 필터 A, B와 패턴을 직접 입력
- MAC 연산 결과(각 필터 점수), 판정 결과, 연산 시간을 출력

2번 (data.json 분석 모드)
- data.json에 정의된 필터와 패턴을 자동으로 로드
- 각 케이스별 MAC 점수, 판정 결과(Cross/X/UNDECIDED), expected 대비 PASS/FAIL 출력
- 전체 성능 분석 및 결과 요약(통과/실패) 제공
<p align="center">&nbsp;</p>

## 3. 구현 방법
### 3-1. 라벨 정규화 방식
```bash
def normalize_label(label: str) -> str:
    label = label.lower()
    if label in ["+", "cross"]:
        return "Cross"
    elif label in ["x"]:
        return "X"
    return "UNKNOWN"
```
입력 데이터의 라벨 표기법이 달라도 같게 처리하기 위해 텍스트를 정규화함 <br>
라벨을 모두 소문자로 바꿔서 +나 cross 라면 Cross 로 바꿔주는 등의 방식을 사용했지만 <br>

```bash
    if label in ["+", "Cross", "cross"]:
        return "Cross"
```
하는 방식도 있음 
<p align="center">&nbsp;</p>

### 3-2. MAC 연산
```bash
def mac_operation_2d(pattern, filter):
    total = 0.0
    n = len(pattern)
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filter[i][j]
    return total
```

```bash
def mac_operation_1d(pattern_1d, filter_1d):
    total = 0.0
    size = len(pattern_1d)
    for i in range(size):
        total += pattern_1d[i] * filter_1d[i]
    return total
```
패턴 매칭 및 스코어 계산을 위해 각 요소의 곱을 모두 더함
<p align="center">&nbsp;</p>

### 3-3. 동점 처리 정책 (epsilon)
```bash
def compare_scores_mode1(a, b):
    # A vs B
    if abs(a - b) < EPSILON:
        return "UNDECIDED"
    return "A" if a > b else "B"
```

```bash
def compare_scores_mode2(cross_score, x_score):
    # Cross vs X
    if abs(cross_score - x_score) < EPSILON:
        return "UNDECIDED"
    return "Cross" if cross_score > x_score else "X"
```
컴퓨터는 모든 숫자를 0과 1로 저장하므로 10진수 소수는 이진수로 변환할 때 무한 소수가 되는 경우가 많음 
<p>
    <img width="702" height="240" alt="Screenshot 2026-04-21 at 1 51 26 PM" src="https://github.com/user-attachments/assets/a59352c8-da3f-4c33-a006-ab722bc13a21" />
</p>
0.1과 0.2를 이진수로 바꾸면 무한 소수가 되는데, 컴퓨터가 메모리 한계 상 중간에 잘라버리는(Rounding Error) 과정에서 미세한 찌꺼기 값이 남아있게됨 <br>
0.0001100110011 ... 이런 무한한 소수를 저장할 공간이 부족하므로 뒤를 강제로 자르는데, 마지막 비트에서 반올림이 발생할 때 원래 값보다 미세하게 크거나 작은 값이 저장됨  <br>

그래서 이 정도면 같다고 치자~ 같은 마인드로 Epsilon을 사용함  <br>
우리가 허용할 수 있는 최소한의 오차 범위를 두는 것임  <br>
<p align="center">&nbsp;</p>

#### **Epsilon 외에 오차를 다루는 다른 방식들**
- 정수 연산 : 소수점 이하 자릿수를 없애기 위해 전체에 100이나 1000을 곱해 정수로 변환하여 계산한 뒤, 마지막에 다시 나누는 방식
  
- 분수 연산 : 숫자를 소수가 아닌 분수 형태로 저장 (0.3333... 대신 1/3로 저장)
<p>
    <img width="911" height="259" alt="Screenshot 2026-04-21 at 2 05 48 PM" src="https://github.com/user-attachments/assets/72a5da77-be83-48f6-96e1-bb27a92af9f0" />
</p>
<br>

- Decimal 연산 : 10진법 계산 방식
<p>
    <img width="701" height="234" alt="Screenshot 2026-04-21 at 2 04 09 PM" src="https://github.com/user-attachments/assets/c48da989-12f1-4ba9-8102-cc426ab2bbf5" />
</p>
<br>

- 가변 엡실론 : 두 수의 크기에 비례해서 오차 범위를 유동적으로 조절하는 방식 (고정된 엡실론(1e-9)은 숫자가 아주 작을 때는 너무 큰 오차가 되고, 숫자가 수조 단위로 클 때는 너무 작은 오차가 되므로)
<br>
<p align="center">&nbsp;</p>


## 4. 결과 리포트 
### 4-1. 실패 케이스 
원인 

### 4-2. 최적화 전/후 성능 비교
<p>
    <img width="501" height="172" alt="Screenshot 2026-04-16 at 2 37 56 PM" src="https://github.com/user-attachments/assets/6c378fb3-bbcf-4833-8b01-34f70c1eb51a" />
</p>
모든 크기에서 1차원 배열 방식이 더 빠른 성능을 보였다. <br>

2D 배열 방식은 리스트 안에 리스트가 있는 구조여서 추가 인덱싱이 발생하지만, <br>
1D 배열 방식은 연속된 메모리에 접근하여 CPU 캐시 활용 효율이 증가해서 속도가 향상된 것으로 보인다. 
<p align="center">&nbsp;</p>

## 5. 트러블슈팅
### 5-1. 데이터 행/열 수 불일치 
data.json 패턴 size_25_1 중에서 
<p>
    <img width="620" height="103" alt="Screenshot 2026-04-16 at 11 58 34 AM" src="https://github.com/user-attachments/assets/a81d3ff9-dcbe-4348-8c53-37c463d8150a" />
</p>
X 필터인데도 Cross로 판정되는 오류가 발생했음 <br>
알고보니 행 수가 1개 부족했던 것이었고, <br>
패턴을 자동으로 생성하는 기능의 필요성을 느꼈음 

<p align="center">&nbsp;</p>

### 5-2. 빈 데이터 
<p>
    <img width="148" height="183" alt="Screenshot 2026-04-21 at 8 27 49 AM" src="https://github.com/user-attachments/assets/133cd3ae-287e-41db-a76e-b9b0adae4575" />
</p>

데이터가 비어있을 경우, 

<p>
    <img width="483" height="66" alt="Screenshot 2026-04-21 at 8 20 31 AM" src="https://github.com/user-attachments/assets/9883e5d3-ed02-485c-ba54-c132446eb5b8" />
</p>

실패원인이 list out of range 로 뜨길래 

<p>
    <img width="396" height="80" alt="Screenshot 2026-04-21 at 9 20 54 AM" src="https://github.com/user-attachments/assets/793a8424-1876-4985-8547-8ac52fb6fee8" />
</p>
빈 데이터가 나오는 경우를 추가하여 처리했음 

<p align="center">&nbsp;</p>

## 6. 보충 설명 
### 모드 1 입력 검증 
```bash
def input_matrix(n, name):
    print(f"{name} ({n}줄 입력, 공백 구분)")
    matrix = []
    while True:
        matrix.clear()
        try:
            for _ in range(n):
                row = list(map(float, input().split()))

                # 열 개수 검증 
                if len(row) != n:
                    raise ValueError
                matrix.append(row)
            print()
            return matrix
        except:
            print("입력 형식 오류 : 각 줄에 {}개의 숫자를 공백으로 구분해 입력하세요.".format(n))
```
- n번만큼 행 입력을 받게 강제해서 행 개수 검증

<br>

- 숫자 파싱 검증 : <br>
map(float, ...) : 리스트의 각 요소를 float()에 전달 <br>
문자가 입력되면 float() 때문에 ValueError 발생

<br>

- TypeError VS ValueError

| 에러 유형 | 발생 상황 | 예시 |
|:---:|:---:|:---:|
| **TypeError** | 아예 취급하지 않는 타입을 넣었을 때 | float([1, 2]) (리스트는 변환 불가) |
| **ValueError** | 타입은 맞지만 내용물이 이상할 때 | float("apple") |

<br>

- list(map(float, input().split())) 흐름

| 코드 | 결과 | 
|:---:|:---:|
| **input()** | "1 0 1" | 
| **input().split()** | ["1", "0", "1"] | 
| **map(float, input().split())** | 실제 변환된 값이 눈에 보이지 않는 map object 상태 |
| **list(map(float, input().split()))** | [1.0, 0.0, 1.0] | 
 

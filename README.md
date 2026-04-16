# Mini NPU Simulator 개발

## 1. 프로젝트 개요
MAC 연산을 구현하여 패턴과 필터 간 유사도를 계산하고, 3x3부터 25x25까지 다양한 크기의 데이터를 판별하는 mini NPU 시뮬레이터를 개발하는 프로젝트이다. <br>
데이터 크기에 따라 연산 시간이 어떻게 변하는지 직접 계산해보고, 구현 과정에서 발생하는 문제를 해결해본다. 

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


## 3. 구현 방법

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


## 5. 트러블슈팅
- data.json 패턴 size_25_1 중에서 
<p>
    <img width="620" height="103" alt="Screenshot 2026-04-16 at 11 58 34 AM" src="https://github.com/user-attachments/assets/a81d3ff9-dcbe-4348-8c53-37c463d8150a" />
</p>
X 필터인데도 Cross로 판정되는 오류가 발생했음 <br>
알고보니 행 수가 1개 부족했던 것이었고, <br>
패턴을 자동으로 생성하는 기능의 필요성을 느꼈음 

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
 

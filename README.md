# Mini NPU Simulator 개발

## 1. 프로젝트 개요

## 2. 실행 방법

## 3. 구현 방법

## 4. 결과 리포트 

## 5. 보충 설명 
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
 

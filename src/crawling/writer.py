import os
import csv


def save_csv(books, file_path):
    file_exists = os.path.exists(file_path)

    if not books:
        return None

    # 1차 이슈 발생 경고 지점: 초기 'w'를 사용하여 계속 덮어쓰여져 50건만 남는 문제가 발생 -> 'a'로 수정하여 이어쓰기로 변경
    # 참고: [cs 라이브러리 문서](https://docs.python.org/ko/3/library/csv.html)
    with open(file_path, "a", newline="", encoding="utf-8-sig") as cf:
        writer = csv.DictWriter(
            cf,
            fieldnames=books[0].keys()
        )

        # 2차 이슈 발생 경고 지점: 해당 로직이 없어 50건마다 헤더가 작성되는 문제가 발생 -> 조건문을 사용하고 상단에 파일이 존재하는지 상태를 저장하는 변수 추가
        if not file_exists:
            writer.writeheader()

        writer.writerows(books)

if __name__ == '__main__':
    print('[INFO] 잘못된 접근방식 입니다.')
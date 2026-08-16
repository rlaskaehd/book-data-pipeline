# main.py
import os
import time
import random
from dotenv import load_dotenv

from crawling.collector import check_current_url, get_response, TooManyRequestsError
from crawling.parser import parse_html, parse_books
from crawling.deduplicator import load_seen_keys, check_book_keys, update_seen_keys
from crawling.writer import save_csv
from crawling.checkpoint import load_checkpoint, update_checkpoint


load_dotenv()


def main():

    # 타겟 카테고리 [컴퓨터/모바일, 과학, 경제경영, 인문학, 역사, 요리/살림]
    target_category_ids = [int(cid.strip()) for cid in os.getenv("TARGET_CATEGORY_IDS").split(",")]

    # 타겟 rows
    target_rows = int(os.getenv("TARGET_ROWS"))
    target_category_rows = int(os.getenv("TARGET_CATEGORY_ROWS"))

    # 1페이지에 몇 개의 책을 노출할지 결정 (25, 50)
    view_rows_count = int(os.getenv("VIEW_ROWS_COUNT"))

    # 요청 간 최소/최대 대기 시간
    minimum_sleep = int(os.getenv("MINIMUM_SLEEP"))
    maximum_sleep = int(os.getenv("MAXIMUM_SLEEP"))

    # 카테고리당 필요한 페이지 수 계산
    # target_category_rows가 view_rows_count로 나누어 떨어지지 않는 경우에도
    # 마지막 페이지까지 가져오기 위해 올림 계산
    target_pages = (target_category_rows + view_rows_count - 1) // view_rows_count

    # 데이터 및 체크포인트 경로
    loading_path = os.getenv("LOADING_PATH")
    checkpoint_path = os.getenv("CHECKPOINT_PATH")

    # URL 유효성 검증 -> 실패 시 raise
    url = check_current_url(os.getenv("TARGET_URL"), os.getenv("TARGET_PATH"),)

    # 이전 작업의 체크포인트를 불러옵니다.
    checkpoint = load_checkpoint(checkpoint_path)

    # 체크포인트가 없는 경우 처음부터 시작
    start_index = 0
    start_page = 1

    checkpoint_id = None
    checkpoint_page = None

    # 429 응답이 연속으로 발생한 횟수를 저장합니다.
    # 정상 응답을 받으면 다시 0으로 초기화합니다.
    consecutive_429 = 0

    # checkpoint가 있다면 시작 위치 덮어쓰기
    if checkpoint:
        checkpoint_id = checkpoint["category_id"]
        checkpoint_page = checkpoint["page"]

        # 체크포인트에 저장된 카테고리 위치부터 시작
        start_index = target_category_ids.index(checkpoint_id)

        # 체크포인트는 "해당 페이지까지 완료"라는 의미이므로
        # 다음 페이지부터 작업 시작
        start_page = checkpoint_page + 1

    # 기존 CSV에서 복합 키를 한 번만 읽어와 중복 확인용 set 생성
    seen_keys = load_seen_keys(loading_path)

    # 이미 적재된 데이터의 수
    row_count = len(seen_keys)

    # 이미 목표 row 수를 만족한 경우 작업하지 않고 종료
    if row_count >= target_rows:
        print(f"[INFO] 이미 작업이 완료되었습니다. rows: {row_count}")
        return

    # 루프 시작(카테고리 선택)
    for category_id in target_category_ids[start_index:]:

        # 체크포인트에 기록된 카테고리라면 마지막 완료 페이지 다음부터 시작
        # 그 이후 카테고리부터는 다시 1페이지부터 시작
        page_start = (start_page if category_id == checkpoint_id else 1)

        # 루프 시작(페이지 선택)
        for page in range(page_start, target_pages + 1):

            print(f"""\
[INFO]
 카테고리 ID: {category_id}
 페이지: {page}
 크롤링을 시작합니다
""")

            # 429 응답 발생 시 다음 페이지로 넘어가지 않고
            # 현재 페이지에서 정상 응답을 받을 때까지 재시도합니다.
            while True:
                try:
                    # html text를 가져옵니다.
                    html_text = get_response(
                        url,
                        page=page,
                        cid=category_id,
                        view_rows_count=view_rows_count,
                    )

                    # 정상 응답을 받은 경우 연속 429 발생 횟수를 초기화합니다.
                    consecutive_429 = 0
                    break

                except TooManyRequestsError:
                    # 429 응답이 발생한 경우 연속 발생 횟수를 증가시킵니다.
                    consecutive_429 += 1

                    print(
                        f"[WARNING] 429 응답이 발생했습니다. "
                        f"연속 발생 횟수: {consecutive_429}/3"
                    )

                    # 429 응답이 연속 3회 발생한 경우 서버에 추가 요청을 보내지 않고
                    # 현재 작업을 즉시 종료합니다.
                    if consecutive_429 >= 3:
                        print(
                            "[ERROR] 429 응답이 연속 3회 발생하여 "
                            "작업을 종료합니다."
                        )
                        return

                    # 429 응답 발생 시 60초 동안 대기한 후
                    # 동일한 카테고리와 페이지를 다시 요청합니다.
                    print(
                        "[INFO] 요청 제한으로 인해 60초 대기 후 "
                        "동일 페이지를 다시 요청합니다."
                    )
                    time.sleep(60)

            # BeautifulSoup으로 파싱한 결과물을 가져옵니다.
            html = parse_html(html_text)

            # 본격적인 파싱을 진행 후 view_rows_count 수만큼 리스트로 반환합니다.
            book_list = parse_books(html)

            # 기존 데이터 및 현재 실행 중 수집된 데이터와 비교하여 중복 제거
            unique_book_list = check_book_keys(
                book_list,
                seen_keys,
            )

            # 목표 row 수를 초과하지 않도록 현재 남은 적재 가능 행 수만큼 잘라냅니다.
            remaining_rows = target_rows - row_count
            unique_book_list = unique_book_list[:remaining_rows]

            # 중복 제거가 완료된 데이터를 저장합니다.
            save_csv(
                unique_book_list,
                loading_path,
            )

            # 실제 CSV에 저장된 데이터만 seen_keys에 반영합니다.
            update_seen_keys(
                unique_book_list,
                seen_keys,
            )

            # CSV 저장까지 성공한 페이지를 체크포인트로 기록합니다.
            update_checkpoint(
                checkpoint_path,
                category_id,
                page,
            )

            # 실제 새롭게 적재된 데이터 수만큼 카운트 증가
            row_count += len(unique_book_list)

            # 목표 row 수에 도달하면 전체 작업 즉시 종료
            if row_count >= target_rows:
                print(
                    f"[INFO] 작업이 완료되었습니다. "
                    f"rows: {row_count}"
                )
                return

            # 서버에 연속적으로 요청하지 않도록
            # 설정한 최소/최대 시간 사이의 임의 시간 동안 대기합니다.
            time.sleep(
                random.uniform(
                    minimum_sleep,
                    maximum_sleep,
                )
            )


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"[ERROR] {e}")
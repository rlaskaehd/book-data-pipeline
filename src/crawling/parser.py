import re

from bs4 import BeautifulSoup


def parse_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    return soup

def parse_books(soup):

    # 반환할 책 정보 리스트 {제목, 대표저자, 저자수, 출판사, 출판일, 상세페이지 url, 저자들(list)}
    # 참고: [BeautifulSoup 라이브러리 문서](https://www.crummy.com/software/BeautifulSoup/bs4/doc.ko/#searching-the-tree)
    books = []

    # 크롤링 시작
    book_lists = soup.select('.ss_book_box')

    for book_list in book_lists:
        book_list = book_list.select_one('.ss_book_list')
        il = book_list.select('li')

        # 책 제목하고 URL 발라내기
        title = book_list.select_one('a.bo3').get_text(strip=True).split('(')[0]
        detail_url = book_list.select_one('a.bo3').get('href')

        # 발생 이슈2: 추가 li 때문에 위치 기반 메타데이터 선택 실패
        # -> 구분자 기준으로 메타데이터 행 선택 로직 추가
        metadata_text = next(
            (
                item.get_text('', strip=True)
                for item in il
                if item.get_text('', strip=True).count('|') >= 2
            ),
            None,
        )

        # 발생 이슈4: 일부 상품은 저자 정보가 생략되어
        # '출판사 | 출판일' 형태로 반환됨
        # -> 기존 형식을 우선 탐색하고, 없을 때 출판일 패턴으로 보완 형식 검색
        if metadata_text is None:
            metadata_text = next(
                (
                    item.get_text('', strip=True)
                    for item in il
                    if (
                        item.get_text('', strip=True).count('|') == 1
                        and re.search(
                            r'\d{4}년\s*\d{1,2}월',
                            item.get_text('', strip=True),
                        )
                    )
                ),
                None,
            )

        # 메타데이터 구조를 확인할 수 없는 상품은 건너뜁니다.
        if metadata_text is None:
            continue

        metadata = [
            value.strip()
            for value in metadata_text.split('|', 2)
        ]

        if len(metadata) == 3:
            author_text, publisher, published_date = metadata

            authors = [
                author.strip()
                for author in author_text.split('(')[0].split(',')
                if author.strip()
            ]

        elif len(metadata) == 2:
            publisher, published_date = metadata
            authors = []

        else:
            continue

        # 지은이(복수 list), 대표 지은이, 지은이 수, 출판사, 출판일
        # 추가정보
        # .get_text('', strip=True) 부분을 많은 사람들이 뭐하는건지 모르는데(본인 포함) 이거 태그 안의 모든 텍스트 조각을 가져와서
        # 각 조각들의 (strip=True) 공백을 제거한 후에 ('') 조각들 사이에 아무것도 넣지말고 하나로 합쳐라.

        # 발생 이슈3: 정가 필드 누락
        # -> 가격 행의 첫 번째 가격을 정가로 수집
        price_row = next(
            item
            for item in il
            if item.select_one('.ss_p2')
        )

        price_element = price_row.select_one(
            'span:not(.ss_p2):not(.ss_p)'
        )

        list_price = int(
            price_element.get_text(strip=True).replace(',', '')
        )

        books.append({
            'title': title,
            'primary_author': authors[0] if authors else '',
            'publisher': publisher,
            'published_date': published_date,
            'list_price': list_price,
            'detail_url': detail_url,
            'author_count': len(authors),
            'authors': '|'.join(authors),
            })
    
    return books

if __name__ == '__main__':
    print('[INFO] 잘못된 접근방식 입니다.')

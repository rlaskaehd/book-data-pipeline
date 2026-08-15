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

        def il_rule(i):
            return il[i] if len(il) > 4 else il[i-1]

        # 책 제목하고 URL 발라내기
        title = book_list.select_one('a.bo3').get_text(strip=True).split('(')[0]
        detail_url = book_list.select_one('a.bo3').get('href')
        
        # 지은이(복수 list), 대표 지은이, 지은이 수, 출판사, 출판일
        # 추가정보
        # .get_text('', strip=True) 부분을 많은 사람들이 뭐하는건지 모르는데(본인 포함) 이거 태그 안의 모든 텍스트 조각을 가져와서
        # 각 조각들의 (strip=True) 공백을 제거한 후에 ('') 조각들 사이에 아무것도 넣지말고 하나로 합쳐라.
        authors = il_rule(2).get_text('', strip=True).split('|')[0].split('(')[0].split(',')
        authors = [author.strip() for author in authors]    # 각 저자 사이의 공백 제거
        publisher = il_rule(2).get_text('', strip=True).split('|')[1]
        published_date = il_rule(2).get_text('', strip=True).split('|')[-1]

        books.append({
            'title': title,
            'primary_author': authors[0],
            'publisher': publisher,
            'published_date': published_date,
            'detail_url': detail_url,
            'author_count': len(authors),
            'authors': '|'.join(authors),
            })
    
    return books

if __name__ == '__main__':
    print('[INFO] 잘못된 접근방식 입니다.')
import os
import csv

def make_book_key(book):
    return (
        book["title"],
        book["primary_author"],
        book["publisher"],
        book["published_date"],
    )


def load_seen_keys(file_path):
    seen_keys = set()

    if not os.path.exists(file_path):
        return seen_keys

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for book in reader:
            seen_keys.add(make_book_key(book))
    
    return seen_keys


def check_book_keys(books, seen_keys):
    unique_books = []
    current_keys = set()

    for book in books:
        key = make_book_key(book)

        if key in seen_keys or key in current_keys:
            continue

        current_keys.add(key)
        unique_books.append(book)

    return unique_books

def update_seen_keys(books, seen_keys):
    for book in books:
        seen_keys.add(make_book_key(book))

if __name__ == '__main__':
    print('[INFO] 잘못된 접근방식 입니다.')
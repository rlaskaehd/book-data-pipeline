import os
import json

def load_checkpoint(file_path):

    file_exists = os.path.exists(file_path)
    if not file_exists:
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        state = json.load(f)

    return state


def update_checkpoint(file_path, category_id, page):
    
    # 참고: [json 라이브러리 문서](https://docs.python.org/ko/3.13/library/json.html)
    # 참고: [json 라이브러리 설명 블로그](https://papari1123.github.io/python/JSON/)
    
    state = {'category_id' : category_id, 'page': page}

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    print('[INFO] 잘못된 접근방식 입니다.')

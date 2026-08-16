import requests

class TooManyRequestsError(Exception):
    pass

# 참고: [requests 튜토리얼](https://blog.choonzang.com/it/python/2606/)
def check_current_url(base_url, path):
    url = base_url + path

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        # 참고: [python Docs](https://docs.python.org/3/tutorial/errors.html)
        raise RuntimeError("URL 검증에 실패했습니다.") from None

    return url


def get_response(url, page, cid, view_rows_count=50):
    params = {
        "BrowseTarget": "List",
        "ViewRowsCount": view_rows_count,
        "page": page,
        "CID": cid,
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 429:
            raise TooManyRequestsError('요청 제한이 반환되었습니다.')
        
        response.raise_for_status()

        return response.text
    except requests.exceptions.RequestException:
        raise RuntimeError("데이터 요청에 실패했습니다.") from None

if __name__ == '__main__':
    print('[INFO] 잘못된 접근방식 입니다.')
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from queue import Queue

def web_crawler_bot(url, depth=2):
    visited_urls = set()  # 이미 방문한 URL을 저장하는 집합
    robot_parser = RobotFileParser()  # Robots.txt 파일을 파싱하기 위한 RobotFileParser 객체 생성
    url_queue = Queue()  # 크롤링할 URL을 저장하는 큐

    def is_allowed_by_robots_txt(url):
        base_url = f"{url.scheme}://{url.netloc}"  # URL의 스키마와 호스트 (ex: http://example.com)
        robots_txt_url = urljoin(base_url, "/robots.txt")  # Robots.txt 파일의 URL
        robot_parser.set_url(robots_txt_url)  # RobotFileParser에 Robots.txt 파일의 URL 설정
        robot_parser.read()  # Robots.txt 파일 파싱
        return robot_parser.can_fetch("*", url.geturl())  # 크롤러가 해당 URL을 크롤링해도 되는지 확인

    url_queue.put((url, 1))  # 시작 URL과 깊이 1을 큐에 추가

    while not url_queue.empty():
        current_url, current_depth = url_queue.get()  # 큐에서 URL과 깊이를 가져옴

        if current_depth > depth:  # 크롤링 깊이가 최대 깊이(depth)를 초과하면 종료
            break

        if current_url in visited_urls:  # 이미 방문한 URL인 경우 건너뜀
            continue

        print(f"Crawling {current_url}")
        visited_urls.add(current_url)  # 현재 URL을 방문한 URL 집합에 추가

        try:
            response = requests.get(current_url)  # URL에 HTTP GET 요청을 보냄
            response.raise_for_status()  # HTTP 오류가 발생했을 경우 예외 처리
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            continue
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")  # HTML 문서를 BeautifulSoup으로 파싱

        for link in soup.find_all("a"):  # 모든 anchor 태그(<a>)를 찾아서 링크 추출
            next_url = link.get("href")  # 링크의 href 속성값을 가져옴
            if next_url and next_url.startswith("http"):  # 절대 URL인 경우에만 처리
                next_url = urljoin(current_url, next_url)  # 상대 URL을 절대 URL로 변환
                if next_url not in visited_urls and is_allowed_by_robots_txt(current_url):
                    # 이미 방문한 URL이 아니고, Robots.txt 파일에서 허용된 URL인 경우 큐에 추가
                    url_queue.put((next_url, current_depth + 1))

if __name__ == "__main__":
    starting_url = input("시작할 URL을 입력하세요: ")
    web_crawler_bot(starting_url)  # 시작 URL을 입력받고 크롤러 실행

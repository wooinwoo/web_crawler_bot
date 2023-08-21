import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from queue import Queue


class WebCrawlerBot:
    def __init__(self, starting_url, max_pages=1000):
        self.starting_url = starting_url  # 시작 URL
        self.max_pages = max_pages  # 크롤링할 최대 페이지 수
        self.visited_urls = set()  # 이미 방문한 URL을 저장하는 집합
        self.robot_parser = None  # RobotFileParser
        self.url_queue = Queue()  # 크롤링할 URL을 저장하는 큐

    def fetch(self, url):
        """
        URL에서 데이터를 가져오는 함수
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # HTTP 오류가 발생하면 예외 처리
            return response.text
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
            return None

    def parse_page(self, url, depth):
        """
        URL에서 HTML을 파싱하여 다음 페이지의 URL을 찾고,
        원하는 데이터를 추출하는 작업을 수행하는 함수
        """
        response = self.fetch(url)  # URL에서 데이터 가져오기
        if response:
            soup = BeautifulSoup(response, "html.parser")  # BeautifulSoup으로 HTML 파싱
            # 이곳에서 원하는 데이터 추출 작업 수행
            # 예를 들어, 링크를 찾아 크롤링 대상 URL로 추가
            for link in soup.find_all("a"):
                next_url = link.get("href")
                if next_url and next_url.startswith("http"):  # 절대 URL인 경우에만 처리
                    next_url = urljoin(url, next_url)  # 상대 URL을 절대 URL로 변환
                    next_url_parsed = urlparse(next_url)  # URL을 파싱하여 URL 객체로 변환
                    if (
                        next_url not in self.visited_urls
                        and self.is_allowed_by_robots_txt(next_url_parsed)
                    ):
                        # 이미 방문한 URL이 아니고, Robots.txt 파일에서 허용된 URL인 경우 큐에 추가
                        self.url_queue.put((next_url, depth + 1))

    def is_allowed_by_robots_txt(self, url):
        """
        Robots.txt 파일을 검사하여 크롤러가 해당 URL을 크롤링해도 되는지 확인하는 함수
        """
        base_url = (
            f"{url.scheme}://{url.netloc}"  # URL의 스키마와 호스트 (ex: http://example.com)
        )
        robots_txt_url = urljoin(base_url, "/robots.txt")  # Robots.txt 파일의 URL
        self.robot_parser = RobotFileParser()  # RobotFileParser 객체 생성
        self.robot_parser.set_url(
            robots_txt_url
        )  # RobotFileParser에 Robots.txt 파일의 URL 설정
        self.robot_parser.read()  # Robots.txt 파일 파싱
        return self.robot_parser.can_fetch(
            "*", url.geturl()
        )  # 크롤러가 해당 URL을 크롤링해도 되는지 확인

    def run(self):
        """
        크롤러를 실행하는 함수
        """
        self.url_queue.put((self.starting_url, 1))  # 시작 URL과 깊이 1을 큐에 추가
        while not self.url_queue.empty() and len(self.visited_urls) < self.max_pages:
            current_url, current_depth = self.url_queue.get()  # 큐에서 URL과 깊이를 가져옴
            if current_url in self.visited_urls:  # 이미 방문한 URL인 경우 건너뜀
                continue
            print(f"Crawling {current_url}")
            self.visited_urls.add(current_url)  # 현재 URL을 방문한 URL 집합에 추가
            self.parse_page(
                current_url, current_depth
            )  # 현재 URL에서 HTML 파싱 및 데이터 추출 작업 수행


if __name__ == "__main__":
    starting_url = input("시작할 URL을 입력하세요: ")
    max_pages = int(input("최대 페이지 수를 입력하세요: "))
    crawler = WebCrawlerBot(starting_url, max_pages=max_pages)  # 크롤러 객체 생성
    crawler.run()  # 크롤러 실행

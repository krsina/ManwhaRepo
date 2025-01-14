from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BaseScraper:
    def __init__(self, config):
        self.config = config
        self.driver = self._setup_driver()
        self.book_links = self._read_book_links(config['book_links_file'])

    def _setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
        chrome_options.add_argument("--headless=new")
        return webdriver.Chrome(options=chrome_options)

    def _read_book_links(self, file_path):
        with open(file_path, "r") as file:
            return file.read().splitlines()

    def _get_element(self, locator):
        return WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(locator))

    def _get_text(self, element, css_selector):
        return element.find_element(By.CSS_SELECTOR, css_selector).text

    def _get_attribute(self, element, tag_name, attribute):
        return element.find_element(By.TAG_NAME, tag_name).get_attribute(attribute)

    def scrape(self):
        for book_link in self.book_links:
            self.driver.get(book_link)
            self.scrape_book_details()

    def scrape_book_details(self):
        raise NotImplementedError("Subclasses should implement this method")

    def close(self):
        self.driver.quit()

def create_scraper_instance(config):
    if config['site'] == 'asura':
        return AsuraScraper(config)
    elif config['site'] == 'genz':
        return GenZScraper(config)
    else:
        raise ValueError(f"Unknown site: {config['site']}")

class AsuraScraper(BaseScraper):
    def scrape_book_details(self):
        book_description_element = self._get_element((By.CSS_SELECTOR, self.config['book_desc_css']))
        book_title = self._get_text(book_description_element, self.config['book_title_css'])
        print("Book Title:", book_title)

        chapter_link_div_element = self._get_element((By.CSS_SELECTOR, self.config['chapter_link_css']))
        chapter_link = self._get_attribute(chapter_link_div_element, "a", "href")
        print("Chapter Link:", chapter_link)

        chapter_number = chapter_link.split('/')[-1]
        print("Chapter Number:", chapter_number)
        print()

class GenZScraper(BaseScraper):
    def scrape_book_details(self):
        # Open the URL
        self.driver.get("https://snowmtl.ru/comics/time-limited-genius-dark-knight")  # Replace with the actual URL

        # Print the entire page source for debugging
        print("Page Source:")
        print(self.driver.page_source)
        
        # Wait for the page to fully load
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.entry-title[itemprop="name"]')))
        except Exception as e:
            print(f"Error waiting for book title element: {e}")
        
        # Try to get the book title element
        try:
            book_title_element = self._get_element((By.CSS_SELECTOR, 'h1.entry-title[itemprop="name"]'))
            book_title = book_title_element.text
            print("Book Title:", book_title)
        except Exception as e:
            print(f"Error finding book title element: {e}")

        print()

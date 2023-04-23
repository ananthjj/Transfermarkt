from pathlib import Path
import scrapy

class FreshSpider(scrapy.Spider):
    name = "fresh_spider"
    allowed_domains = ["transfermarkt.com"]
    start_urls = ["https://www.transfermarkt.com"]
    player_drop_down_xpath = "/html/body/div[2]/header/div[2]/tm-quick-select-bar//div/tm-quick-select[4]"
    strings_to_ignore = ["beraterfirma",
    "berater",
    # "gemeinsameSpiele",
    # "leistungsdaten",
    "quote",
    "impressum",
    "intern",
    "news",
    "trainer",
    # "aktuell", 
    "newsarchiv", 
    # "verein", 
    "beliebtheit", 
    "neuestetransfers", 
    # "statistik", 
    "forum", 
    # "wertvollstemannschaften", 
    # "marktwertetop", 
    "whatsMyValue", 
    "unbeliebter", 
    "sort", 
    # "wettbewerb", 
    "transfers", 
    "marktwertverlauf", 
    "index", 
    "spielbericht", 
    # "nationalmannschaft", 
    "geruechte", 
    "debuets", 
    "erfolge",
    "javascript:void(0)"]
    # strings_to_accept = ["profil", "verletzungen"]

    def parse(self, response):
        # If the URL contains the country drop-down, navigate to all options
        # if "quickselect_country" in response.url:
        #     print(f"Entering country drop-down if statement, processing URL: {response.url}")
        #     yield from self.navigate_drop_down(response, "/html/body/div[2]/header/div[2]/tm-quick-select-bar//div/tm-quick-select[1]")

        # # If the URL contains the competition drop-down, navigate to all options
        # elif "wettbewerb" in response.url:
        #     print(f"Entering competition drop-down if statement, processing URL: {response.url}")
        #     yield from self.navigate_drop_down(response, "/html/body/div[2]/header/div[2]/tm-quick-select-bar//div/tm-quick-select[2]")

        # # If the URL contains the club drop-down, navigate to all options
        # elif "verein" in response.url:
        #     print(f"Entering club drop-down if statement, processing URL: {response.url}")
        #     yield from self.navigate_drop_down(response, "/html/body/div[2]/header/div[2]/tm-quick-select-bar//div/tm-quick-select[3]")

        # # If the URL contains the player drop-down and all the drop-downs have been selected, scrape the data
        # elif "profil" in response.url and self.all_drop_downs_selected(response):
        #     print(f"Entering player drop-down if statement, processing URL: {response.url}")
        #     yield {
        #         "title": response.css("title::text").extract_first(),
        #         "body": response.css("p::text").extract()
        #     }

        # else:
            # Extract links from the current page
        for href in response.css("a::attr('href')"):
            url = response.urljoin(href.extract())

            # Ignore pages containing certain strings
            if any(s in url for s in self.strings_to_ignore):
                continue

            # Download pages containing certain strings
            # if any(s in url for s in self.strings_to_accept):
            with open("test.txt", "a") as f:
                f.write(url + "\n")
            yield scrapy.Request(url, callback=self.parse)


    def navigate_drop_down(self, response, drop_down_xpath):
        """
        Navigate through all options of a drop-down menu
        """
        # Find the drop-down element
        drop_down = response.xpath(drop_down_xpath)

        # Get the drop-down options
        drop_down_options = drop_down.xpath(".//div[contains(@class, 'tm-select-results')]/a")

        # Loop through each option
        for option in drop_down_options:
            # Extract the option text and URL
            option_text = option.xpath(".//text()").get()
            option_url = response.urljoin(option.xpath(".//@href").get())

            # Make a request for the option URL if it's in the allowed domains
            if any(domain in option_url for domain in self.allowed_domains):
                yield scrapy.Request(
                    option_url,
                    callback=self.navigate_to_next_drop_down if drop_down_xpath != self.player_drop_down_xpath else self.parse_player,
                    meta={"option_text": option_text}
                )

    def all_drop_downs_selected(self, response):
        """
        Check if all the drop-downs on the page have been selected
        """
        for dropdown in response.css("tm-quick-select"):
            if not dropdown.css(".selected"):
                return False
        return True

    def parse_country(self, response):
        """
        Parse the country page to navigate to competitions
        """
        yield from self.navigate_drop_down(response, "/html/body/div[2]/header/div[2]/tm-quick-select-bar//div/tm-quick-select[1]")

    def parse_competition(self, response):
        """
        Parse the competition page to navigate to clubs
        """
        yield from self.navigate_drop_down(response, "/html/body/div[2]/header/div[2]/tm-quick-select-bar//div/tm-quick-select[3]")

    def parse_club(self, response):
        """
        Parse the club page to navigate to players
        """
        yield from self.navigate_drop_down(response, "/html/body/div[2]/header/div[2]/tm-quick-select-bar//div/tm-quick-select[4]")

    def parse_player(self, response):
        """
        Parse the player page to scrape data
        """
        # Extract data from the current page
        yield {
            "option_text": response.meta["option_text"],
            "title": response.css("title::text").extract_first(),
            "body": response.css("p::text").extract()
        }

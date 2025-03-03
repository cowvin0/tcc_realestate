import scrapy


class PackagescraperSpider(scrapy.Spider):
    name = "packagescraper"
    allowed_domains = ["cran.r-project.org"]
    start_urls = ["https://cran.r-project.org/web/packages/index.html"]

    def parse(self, response):
        pass

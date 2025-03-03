import scrapy


class PackagescraperSpider(scrapy.Spider):
    name = "packagescraper"
    allowed_domains = ["cran.r-project.org"]
    start_urls = ["https://cran.r-project.org/web/packages/index.html"]

    def parse(self, response):
        href = response.css("a[target=_top] ::attr(href)").get()
        follow_url = self.start_urls[0].replace("index.html", "") + href

        yield response.follow(
            follow_url, callback=self.parse_packages_info, dont_filter=True
        )

    def parse_packages_info(self, response):
        get_all_tr = response.css("tr ::text").getall()
        packages_element = [x.strip() for x in get_all_tr if x.strip() != ""][3:]

        pub_date = packages_element[::3]
        packs_name = packages_element[1::3]
        desc_packs = packages_element[2::3]

        for i in zip(pub_date, packs_name, desc_packs):
            yield {
                "publication_date": i[0],
                "package_name": i[1],
                "description_packs": i[2],
            }

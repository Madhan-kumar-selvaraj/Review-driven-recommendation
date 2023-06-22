import re
import os
import json
import time
import codecs
import datetime
import requests
from lxml import html
from urllib import parse
from dateutil.relativedelta import relativedelta


class GoogleReview:
    def __init__(self, search_for, place):
        self.search_for = search_for
        self.place = place
        self.all_reviews = list()
        json_configuration = json.load(open("configuration_scrapers.json"))
        self.google_config = json_configuration.get("google", {})
        self.params = self.google_config.get("params")
        self.cookies = self.google_config.get("cookies")
        self.headers = self.google_config.get("headers")
        self.output_folder_name = self.google_config.get("output_folder_name")
        self.output_filename = self.google_config.get("output_json_filename")

    def date_format(self, collected_doc):
        datetime_format = "%Y-%m-%d %H:%M:%S"
        today = datetime.date.today()
        try:
            timing = collected_doc["review_date"].split(" ")
            if 'hour' in collected_doc["review_date"]:
                return today.strftime(datetime_format)
            if 'day' in collected_doc["review_date"]:
                if timing[0] == 'a':
                    return (today + relativedelta(days=-1)).strftime(datetime_format)
                return (today + relativedelta(days=-int(timing[0]))).strftime(datetime_format)

            if 'week' in collected_doc["review_date"]:
                if timing[0] == 'a':
                    return (today + relativedelta(weeks=-1)).strftime(datetime_format)
                return (today + relativedelta(weeks=-int(timing[0]))).strftime(datetime_format)

            if 'month' in collected_doc["review_date"]:
                if timing[0] == 'a':
                    return (today + relativedelta(months=-1)).strftime(datetime_format)
                return (today + relativedelta(months=-int(timing[0]))).strftime(datetime_format)

            if 'year' in collected_doc["review_date"]:
                if timing[0] == 'a':
                    return (today + relativedelta(years=-1)).strftime(datetime_format)
                return (today + relativedelta(years=-int(timing[0]))).strftime(datetime_format)

        except Exception as date_format_error:
            print(f"Exception in date_format_error: {date_format_error}")
            return today.strftime(datetime_format)

    def review_parsing(self, response, user_input, url):
        tree = html.fromstring(response.text)
        reviews = []
        entity_name = "".join(tree.xpath('//div[@class="P5Bobd"]//text()'))
        address = "".join(tree.xpath('//div[@class="T6pBCe"]//text()'))
        for iterative in tree.xpath('//div[@class="WMbnJf vY6njf gws-localreviews__google-review"]'):
            name = "".join(iterative.xpath('.//div[@class="jxjCjc"]//div[@class="TSUbDb"]//text()'))
            rate = "".join(
                iterative.xpath(
                    './/div[@class="jxjCjc"]//div[@class="PuaHbe"]//span[@class="Fam1ne EBe2gf"]/@aria-label'))
            review_date = "".join(iterative.xpath('.//div[@class="jxjCjc"]//div[@class="PuaHbe"]//text()'))
            text = " ".join(iterative.xpath('.//div[@class="jxjCjc"]//span[@class="review-full-text"]//text()'))
            if not text:
                text = " ".join(iterative.xpath('.//div[@class="jxjCjc"]//div[@class="Jtu6Td"]//text()'))
            imges = ",".join([j.replace('background-image:url(', '').replace(')', '').replace('w100', 'w1000').replace(
                'h100', 'h1000') for j in iterative.xpath('.//div[@class="DQBZx"]//div[@role="img"]/@style')])
            reviews.append({
                'user_search_keyword': self.params["q"],
                'input': codecs.decode(user_input.replace("\\\\","\\"), 'unicode_escape'),
                "user": name,
                "rating": rate,
                'review_date': review_date.replace('New', ''),
                'formatted_review_date': self.date_format({'review_date': review_date.replace('New', '')}),
                "review_text": parse.unquote(text),
                'name': parse.unquote(entity_name),
                'address': parse.unquote(address),
                "images": imges,
                "review_availability": True,
                "url": parse.unquote(url),
                "extraction_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        next_token = re.search('data-next-page-token="(.*?)"', response.text).group(1)
        return {
            "next_token": next_token,
            "reviews": reviews
        }

    def next_req(self, response, input_data, main_url):
        each_review_count = 0
        feature_id = re.search('data-fid="(.*?)"', response.text).group(1)
        vet = "12ahUKEwjjpoL-jaL3AhVGUGwGHcyVCNgQxyx6BAgBED0..i"
        ved = re.search('data-ved="(.*?)"', response.text).group(1)
        next_token = re.search('data-next-page-token="(.*?)"', response.text).group(1)
        rv = self.review_parsing(response, input_data, main_url)
        for iterative in rv['reviews']:
            # print(iterative)
            each_review_count += 1
            self.all_reviews.append(iterative)
        while next_token:
            url = f'https://www.google.com/async/reviewSort?vet={vet}&ved={ved}&yv=3&async=feature_id:{feature_id},review_source:All%20reviews,sort_by:qualityScore,is_owner:false,filter_text:,associated_topic:,next_page_token:{next_token},_pms:s,_fmt:pc'
            response = requests.get(url, headers=self.headers, cookies=self.cookies)
            res = self.review_parsing(response, input_data, main_url)
            next_token = res['next_token']
            for iterative in res['reviews']:
                each_review_count += 1
                # print(iterative)
                self.all_reviews.append(iterative)
        print(f"Total number of reviews fetched for '{input_data}' is {each_review_count}")

    def get_ids_by_query_name(self, query):
        time.sleep(5)
        url = f'https://www.google.com/search?q={parse.quote(query)}'
        r = requests.get(url, headers=self.headers, cookies=self.cookies)
        try:
            feature_id = re.search('data-fid="(.*?)"', r.text).group(1)
            try:
                eid = re.search('input value="(.*?)" name="ei"', r.text).group(1)
            except:
                eid = re.search('input value\\x3d\\x22(.*?)" name\\x3d\\x22ei\\x22', r.text).group(1)
            feature_eid = {
                "feature_id": feature_id,
                "eid": eid
            }
            return feature_eid
        except:
            return {}

    def review_requests(self, input_values):
        for index, user_input in enumerate(input_values):
            if not str(self.place).lower() in str(user_input).lower():
                user_input = f"{user_input} {self.place}"
            time.sleep(5)
            try:
                print(f"Started scraping reviews for '{user_input}'")
                ids = self.get_ids_by_query_name(user_input)
                main_url = f"https://www.google.com/search?q={user_input}#lrd={ids['feature_id']},1,,,"
                if ids:
                    ei = ids["eid"]
                    feature_id = ids["feature_id"]
                    response = requests.get(
                        f'https://www.google.com/async/reviewDialog?ei={ei}&yv=3&async=feature_id:{feature_id},review_source:All%20reviews,sort_by:qualityScore,is_owner:false,filter_text:,associated_topic:,next_page_token:,async_id_prefix:,_pms:s,_fmt:pc',
                        headers=self.headers, cookies=self.cookies)
                    self.next_req(response, user_input, main_url)
                else:
                    print(f"No reviews available for the input provided <{user_input}>, please check the input again.")
            except Exception as review_requests_error:
                print(f"Exception in start_requests_error: {review_requests_error}")
        return self.all_reviews

    def start_requests(self):
        self.params["q"] = f"{self.search_for} at {self.place}"
        response = requests.get('https://www.google.com/maps', params=self.params, headers=self.headers)
        if response.ok and response.content:
            tree = html.fromstring(response.content)
            try:
                rows_block = tree.xpath('//link[@rel="shortcut icon"]/following-sibling::script[1]')[0].text
                results_list = re.findall(r'''"SearchResult.TYPE_.*?],\\+"(.*?)\\+"''', rows_block)
                print(results_list)
                if results_list:
                    self.review_requests([results_list[1]])
                if len(self.all_reviews) > 0:
                    filename = f"{self.output_filename}_{str(datetime.date.today())}.json"
                    if not os.path.exists(self.output_folder_name):
                        os.mkdir(self.output_folder_name)
                    if os.path.exists(f"{self.output_folder_name}/{filename}"):
                        os.remove(f"{self.output_folder_name}/{filename}")
                    with open(f"{self.output_folder_name}/{filename}", "a+") as new_file:
                        for each_row in self.all_reviews:
                            new_file.write(json.dumps(each_row))
                            new_file.write("\n")
                print(f"Total number of reviews fetched across all the links is {len(self.all_reviews)}")
            except Exception as error:
                print(error)


start = time.time()
obj = GoogleReview(search_for='hospital', place="erode")
obj.start_requests()
end = time.time()
print(f'Scraper took total of {end - start} seconds')

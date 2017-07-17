import json
import requests

from flask import Flask, render_template, request
app = Flask(__name__)


class RequestError(Exception):
    pass


class ParsingError(Exception):
    pass


class StackOverflowClient(object):

    API_URL = "https://api.stackexchange.com/"
    VERSION = "2.2"

    def get_so_posts_by_user_id(self, user_id):
        all_posts = []
        page_counter = 1
        while True:
            try:
                r = requests.get(
                    "{api_url}/{version}/users/{user_id}/posts?"
                    "page={page}&site=stackoverflow&order=desc&"
                    "sort=activity".format(
                        api_url=self.API_URL, version=self.VERSION,
                        user_id=user_id, page=page_counter
                    )
                )
            except Exception as e:
                raise RequestError(e)
            else:
                if r.status_code == 200:
                    try:
                        new_posts, has_more = self.parse_posts(r.text)
                        all_posts.extend(new_posts)
                        page_counter += 1

                        if not has_more:
                            break
                    except ParsingError as e:
                        break
                else:
                    break
        return all_posts

    def parse_posts(self, data):
        posts = []
        try:
            parsed_data = json.loads(data)
            for item in parsed_data["items"]:
                posts.append(item["link"])

            has_more = parsed_data["has_more"]
        except Exception as e:
            raise ParsingError(e)
        else:
            return posts, has_more


@app.route('/', methods=['GET', 'POST'])
def index():
    posts = []
    if request.method == 'POST':
        if request.form['user_id']:
            so_client = StackOverflowClient()
            posts = so_client.get_so_posts_by_user_id(request.form['user_id'])
    return render_template('index.html', posts=posts)

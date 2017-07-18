import json
import requests
import config


class RequestError(Exception):
    pass


class ParsingError(Exception):
    pass


class StackOverflowClient(object):

    API_URL = "https://api.stackexchange.com/"
    VERSION = "2.2"
    ACCESS_TOKEN_URL = "https://stackexchange.com/oauth/access_token/json"
    OAUTH_URL = "https://stackexchange.com/oauth"

    CLIENT_ID = config.CLIENT_ID
    CLIENT_SECRET = config.CLIENT_SECRET
    KEY = config.KEY

    def get_so_posts_by_user_id(self, user_id):
        url = "{api_url}{version}/users/{user_id}/posts?site=stackoverflow" \
              "&order=desc&sort=activity".format(
            api_url=self.API_URL, version=self.VERSION,
            user_id=user_id
        )
        return self.get_so_posts(url=url)

    def get_so_posts(self, url):
        all_posts = []
        page_counter = 1
        while True:
            try:
                page_url = "{url}&page={page}".format(url=url, page=page_counter)
                r = requests.get(page_url)
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

    def get_oauth_url(self, redirect_url):
        return "{url}?client_id={client_id}&redirect_uri={redirect_url}".format(
            url=self.OAUTH_URL, client_id=self.CLIENT_ID, redirect_url=redirect_url
        )

    def get_access_token(self, redirect_url, code):
        full_url = "{url}?" \
               "client_id={client_id}&" \
               "client_secret={client_secret}&" \
               "code={code}&" \
               "redirect_uri={redirect_url}".format(
            url=self.ACCESS_TOKEN_URL,
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            code=code,
            redirect_url=redirect_url
        )

        r = requests.post(full_url)
        if r.status_code == 200:
            try:
                parsed_data = json.loads(r.text)
                return parsed_data["access_token"]
            except Exception as e:
                return None
        else:
            return None

    def get_own_posts(self, token):
        url = "{api_url}{version}/me/posts?key={key}&site=stackoverflow&order=desc&" \
              "sort=activity&access_token={token}".format(
            api_url=self.API_URL, version=self.VERSION, key=self.KEY, token=token
        )
        return self.get_so_posts(url=url)

    def get_user_details(self, token):
        url = "{api_url}{version}/me?key={key}&site=stackoverflow&order=desc&" \
              "sort=reputation&access_token={token}".format(
            api_url=self.API_URL, version=self.VERSION, key=self.KEY, token=token
        )

        try:
            r = requests.get(url)
        except Exception as e:
            raise RequestError(e)
        else:
            if r.status_code == 200:
                return self.parse_user_details(r.text)
            else:
                return None

    def parse_user_details(self, data):
        try:
            parsed_data = json.loads(data)
            for item in parsed_data["items"]:
                return item
        except Exception as e:
            return None

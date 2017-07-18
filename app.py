from flask import Flask, render_template, request, redirect

from api_interaction import StackOverflowClient

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    posts = []
    if request.method == 'POST':
        if request.form['user_id']:
            so_client = StackOverflowClient()
            posts, user_details = so_client.get_so_posts_by_user_id(request.form['user_id'])
    return render_template('index.html', posts=posts)


@app.route('/own_posts', methods=['GET', 'POST'])
def own_posts():
    so_client = StackOverflowClient()
    if request.method == 'POST':
        return redirect(so_client.get_oauth_url(request.base_url), code=302)
    else:
        access_token = so_client.get_access_token(request.base_url, request.args.get('code'))
        posts = []
        user_details = None
        if access_token:
            posts, user_details = so_client.get_own_posts(access_token)
        return render_template('own_posts.html', posts=posts, user_details=user_details)


if __name__ == '__main__':
    app.run()

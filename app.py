from flask import Flask, request, jsonify
from flask.views import MethodView
import tweepy
from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import random
from flask_apscheduler import APScheduler

load_dotenv()

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)

app.config.from_object(Config)
scheduler = APScheduler()
scheduler.init_app(app)

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
DEBUG = os.getenv("DEBUG", True)


# Twitter client and OpenAI client initialization
twitter_client = tweepy.Client(bearer_token=BEARER_TOKEN, 
                               consumer_key=API_KEY, 
                               consumer_secret=API_SECRET, 
                               access_token=ACCESS_TOKEN, 
                               access_token_secret=ACCESS_SECRET)

client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/ping')
def home():
    return "Pong"
class GenerateTweetAPI(MethodView):
    def post(self):
        data = request.json
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "Invalid prompt"}), 400

        formatted_prompt = f"Generate tweet based on prompt topic: {prompt}"
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=formatted_prompt,
            max_tokens=280,
            temperature=0.7
        )
        tweet = str(response.choices[0].text).strip()[:280] 

        try:
            twitter_client.create_tweet(text=tweet)
            return jsonify({"message": "Tweet posted successfully!", "tweet": tweet})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

class GetUserTweetsAPI(MethodView):
    def get(self):
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        params = {"max_results": 100}
        
        try:
            tweets = twitter_client.get_users_tweets(id=user_id, **params)
            tweet_data = [
                {
                    "tweet_id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "user": tweet.user.username,
                    "profile_image_url": tweet.user.profile_image_url,
                }
                for tweet in tweets.get("data", [])
            ]
            if not tweet_data:
                return jsonify({"message": "No tweets found for this user."})

            return jsonify({"tweets": tweet_data})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


class GetUserIdsAPI(MethodView):
    def get(self):
        usernames = request.args.get('usernames')
        if not usernames:
            return jsonify({"error": "No usernames provided"}), 400
        
        usernames_list = usernames.split(',')
        user_ids = {
            username: self.get_user_id(username) or "Not found or error"
            for username in usernames_list
        }

        return jsonify(user_ids)

    def get_user_id(self, username):
        """Fetches the user ID for a given username."""
        url = f"https://api.twitter.com/2/users/by?usernames={username}"
        headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            return user_data.get('data', [{}])[0].get('id') 
        return None

def generate_tweet_with_random_prompt():
    """
    Generates and posts a tweet using a randomly selected category.
    """
    prompt_categories = ["technology", "creative", "inspirational", "philosophy", "education"]
    chosen_category = random.choice(prompt_categories)
    formatted_prompt = f"Generate tweet based on the prompt topic: {chosen_category}"
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=formatted_prompt,
        max_tokens=280,
        temperature=0.7
    )
    tweet = str(response.choices[0].text).strip()[:280]
    try:
        twitter_client.create_tweet(text=tweet)
        print(f"Tweet posted successfully! Category: {chosen_category} | Tweet: {tweet}")
    except Exception as e:
        print(f"Failed to post tweet: {str(e)}")

# Register class-based views
app.add_url_rule('/generate-tweet', view_func=GenerateTweetAPI.as_view('generate_tweet'))
app.add_url_rule('/get-user-tweets', view_func=GetUserTweetsAPI.as_view('get_user_tweets'))
app.add_url_rule('/get_user_ids', view_func=GetUserIdsAPI.as_view('get_user_ids'))

#Uncomment below code to enable the scheduler
# scheduler.add_job(
#     id="TweetScheduler",
#     func=generate_tweet_with_random_prompt,
#     trigger="interval",
#     minutes=15
# )


if __name__ == '__main__':
    # scheduler.start()
    app.run(debug=DEBUG)

    

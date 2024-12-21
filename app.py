from flask import Flask, request, jsonify
import tweepy
from openai import OpenAI

from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
DEBUG = os.getenv("DEBUG", True)


# auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
# auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
twitter_client = tweepy.Client(bearer_token=BEARER_TOKEN,consumer_key=API_KEY,consumer_secret=API_SECRET,access_token=ACCESS_TOKEN,access_token_secret=ACCESS_SECRET)
client = OpenAI(api_key=OPENAI_API_KEY)


def post_tweet(tweet_content):
    url = "https://api.x.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, json=tweet_content)

        if response.status_code == 201:  # 201 means tweet successfully posted
            print("Tweet posted successfully!")
            print("Tweet ID:", response.json())
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

@app.route('/generate-tweet', methods=['POST'])
def generate_tweet():
    data = request.json
    prompt = data.get("prompt", "Write a tweet about technology.")
    response = client.completions.create(model="gpt-3.5-turbo-instruct",
    prompt=prompt,
    max_tokens=280,
    temperature=0.7)
    tweet = response.choices[0].text.strip()

    try:
        twitter_client.create_tweet(text=tweet)
        return jsonify({"message": "Tweet posted successfully!", "tweet": tweet})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get-tweets', methods=['GET'])
def get_tweets():
    username = request.args.get("username", "twitter")  # Default to 'twitter' if no username is provided
    try:
        # Fetch the 10 most recent tweets from the user's timeline
        tweets = twitter_client.user_timeline(screen_name=username, count=10, tweet_mode='extended')
        tweet_data = [{"tweet": tweet.full_text, "created_at": tweet.created_at} for tweet in tweets]

        return jsonify({"tweets": tweet_data})

    except tweepy.TweepError as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-user-tweets', methods=['GET'])
def get_user_tweets():
    # Retrieve user ID from the query parameters
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    params = {
        "max_results": 100  # Limit to 10 tweets for this request
    }

    try:
        # Call the get_users_tweets method to retrieve the user's tweets
        tweets = twitter_client.get_users_tweets(id=user_id, **params)

        tweet_data = [
            {
                "tweet_id": tweet.id,
                "text": tweet.text,
                "created_at": tweet.created_at,
                "user": tweet.user.username,
                "profile_image_url": tweet.user.profile_image_url,
            }
            for tweet in tweets["data"]  # Assuming 'data' contains tweet information
        ]
        
        return jsonify({"tweets": tweet_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_user_id(username):
    """Fetches the user ID for a given username."""
    url = f"https://api.twitter.com/2/users/by?usernames={username}"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        if "data" in user_data:
            return user_data['data'][0]['id']
        else:
            return None  # User not found
    else:
        return None  # Handle errors (rate limits, etc.)

@app.route('/get_user_ids', methods=['GET'])
def get_user_ids():
    """Endpoint to get Twitter user IDs from usernames."""
    usernames = request.args.get('usernames')
    
    if not usernames:
        return jsonify({"error": "No usernames provided"}), 400
    
    # Split usernames by comma and get user IDs
    usernames_list = usernames.split(',')
    user_ids = {}
    
    for username in usernames_list:
        user_id = get_user_id(username)
        if user_id:
            user_ids[username] = user_id
        else:
            user_ids[username] = "Not found or error"
    
    return jsonify(user_ids)


if __name__ == '__main__':
    app.run(debug=DEBUG)

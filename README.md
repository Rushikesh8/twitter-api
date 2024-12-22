## Twitter Integration with OpenAI

This project is a Flask-based web application that integrates with the Twitter API and OpenAI's GPT models to generate and post tweets automatically. It offers the following features:

- Generate a tweet based on a prompt using OpenAI's GPT-3.5.
- Fetch the latest tweets from a user's Twitter account.
- Retrieve Twitter user IDs based on usernames.

## Features

- **Generate Tweet**: Generate a tweet based on a prompt passed to the API, which is then posted to Twitter.
- **Get User Tweets**: Retrieve the latest tweets from a Twitter user, given their user ID.
- **Get User IDs**: Retrieve the Twitter user ID from a given username or list of usernames.
- **Scheduled Tweet Generation and Posting**: Automatically triggers every 15 minutes using APScheduler.


## Requirements

- Python 3.7+
- Flask
- Tweepy (for Twitter API interaction)
- OpenAI (for text generation)
- Requests (for making HTTP requests)
- python-dotenv (for managing environment variables)

## Setup

Follow these steps to set up and run the project locally:

### 1. Clone the repository

```bash
git clone https://github.com/Rushikesh8/twitter-api.git
cd twitter-api
```

### 2. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # For macOS/Linux
# venv\Scripts\activate   # For Windows

# Install the dependencies
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a .env file in the project’s root directory with the following variables:
```bash
API_KEY=your_twitter_api_key
API_SECRET=your_twitter_api_secret_key
ACCESS_TOKEN=your_twitter_access_token
ACCESS_SECRET=your_twitter_access_token_secret
OPENAI_API_KEY=your_openai_api_key
BEARER_TOKEN=your_twitter_bearer_token
DEBUG=True 
```

### 4. Run the Flask app
```bash
python app.py
```
The app will start running on http://127.0.0.1:5000/.


## API Endpoints

1. POST /generate-tweet

Request Body (JSON)

```bash
{
  "prompt": "Write a tweet about the importance of AI."
}
```
Response (JSON)

```bash 
{
  "message": "Tweet posted successfully!",
  "tweet": "AI is transforming the world! #AI #MachineLearning"
}
```

2. GET /get-user-tweets
Fetch the latest tweets from a Twitter user by their user ID.

Query Parameters
user_id: The Twitter user ID to retrieve tweets for.

Example Request

```bash
GET /get-user-tweets?user_id=1234567890
```

Response (JSON)

```bash 
{
  "tweets": [
    {
      "tweet_id": "1234567890123456789",
      "text": "Just had a great coffee!",
      "created_at": "2024-12-20T14:30:00Z",
      "user": "username",
      "profile_image_url": "https://example.com/profile.jpg"
    }
  ]
}
```

3. GET /get_user_ids
Retrieve the user IDs for a list of Twitter usernames.

Query Parameters
usernames: A comma-separated list of Twitter usernames.

Example Request

```bash
GET /get_user_ids?usernames=jack,elonmusk
```

Response (JSON)

```bash 
{
  "jack": "1234567890",
  "elonmusk": "9876543210"
}
```




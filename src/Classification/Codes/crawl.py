import requests
import os
import csv
import json

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
# bearer_token = os.environ.get("BEARER_TOKEN")
API_KEY = ''
API_SECRET_KEY = ''
bearer_token = ''
ABSPATH = os.path.abspath(os.getcwd())
CSV_FILE = os.path.join(ABSPATH, 'tweets.csv')
tweets_arr = []

# r = requests.post('https://api.twitter.com/oauth2/token',
#                   auth=(API_KEY, API_SECRET_KEY),
#                   headers={'Content-Type':
#                                'application/x-www-form-urlencoded;charset=UTF-8'},
#                   data='grant_type=client_credentials')
# assert r.json()['token_type'] == 'bearer'
# bearer = r.json()['access_token']

# r = requests.get(search_url, headers={'Authorization': 'Bearer ' + bearer})
# print(r.json())


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def failsave(symbol):
    f = open("failsave.txt", "w")
    f.write(symbol)
    f.close()


def connect_to_endpoint(url, headers, hashtag, company_name):
    filters = ' -filter:retweets'
    verified = '-verified: True'
    number_of_tweets = 50
    search_url = url + "?q=%23" + hashtag + ' OR ' + company_name + ' ' + filters + '&lang=en&count=' + str(number_of_tweets) + '&tweet_mode=extended'
    response = requests.request("GET", search_url, headers=headers)

    if response.status_code == 200:
        print(hashtag)
    else:
        generate_csv(tweets_arr)
        failsave(hashtag)
        raise Exception(response.status_code, response.text)

    return response.json()


def get_tweeter_datas(hashtag, company_name):
    url = "https://api.twitter.com/1.1/search/tweets.json"
    headers = create_headers(bearer_token)
    json_response = connect_to_endpoint(url, headers, hashtag, company_name)
    # print(json.dumps(json_response, indent=4, sort_keys=True))
    return json_response

def generate_csv(tweets_arr):
    try:
        with open(CSV_FILE, 'a') as csvfile:
            writer = csv.writer(csvfile)
            # writer.writerow(['Text', 'Datetime', 'Symbol'])
            for dict in tweets_arr:
                writer.writerow([dict['text'], dict['datetime'], dict['symbol'], dict['company_names']])
    except IOError:
        print("I/O error")

    print('done')


def main():
    # f = open('twitter_sample.json',)
    # data = json.load(f)
    # f.close()

    hashtag = ''
    company_name = ''
    bool_failsave = False

    with open('stocks_companies.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            hashtag = row[0]
            company_name = row[1]

            failsave_f = open("failsave.txt", "r")
            lastsaved = failsave_f.read()

            if lastsaved == hashtag or lastsaved == '':
                bool_failsave = True

            if bool_failsave:
                data = get_tweeter_datas(hashtag, company_name)

                for tweet in data['statuses']:
                    text = tweet['full_text']
                    datetime = tweet['created_at']
                    symbol = hashtag
                    tweets_arr.append({
                        'text': text,
                        'datetime': datetime,
                        'symbol': symbol,
                        'company_names': company_name
                    })

        generate_csv(tweets_arr)

if __name__ == "__main__":
    main()
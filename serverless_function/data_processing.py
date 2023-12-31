import pandas as pd
import requests
import boto3
import os

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

def get_restaurants (df, country_codes_df):

    # Create an empty DataFrame for restaurants
    restaurants_df = pd.DataFrame(columns=['Restaurant Id', 'Restaurant Name', 'Country Id', 'City', 'User Rating Votes', 'User Aggregate Rating', 'Cuisines'])

    for restaurants in df.restaurants:
        if len(restaurants) > 0:
            for restaurant in restaurants:
                # Restaurant Id
                restaurant_id = restaurant['restaurant']['R']['res_id']
                # Restaurant Name
                restaurant_name = restaurant['restaurant']['name']
                # Country Id
                country_id = restaurant['restaurant']['location']['country_id']
                # City
                city = restaurant['restaurant']['location']['city']
                # User Rating Votes
                user_rating_votes = restaurant['restaurant']['user_rating']['votes']
                # User Aggregate Rating
                user_aggregate_rating = restaurant['restaurant']['user_rating']['aggregate_rating']
                # Cuisines
                cuisines = restaurant['restaurant']['cuisines']

                # Create a row for the DataFrame
                row = {'Restaurant Id': restaurant_id, 'Restaurant Name': restaurant_name, 'Country Id': country_id, 'City': city, 'User Rating Votes': user_rating_votes, 'User Aggregate Rating': user_aggregate_rating, 'Cuisines': cuisines}
                restaurants_df = pd.concat([restaurants_df, pd.DataFrame([row])], ignore_index=True)

    # Merge with country codes
    restaurants_df = pd.merge(restaurants_df, country_codes_df, left_on="Country Id", right_on="Country Code", how="left")
    restaurants_df = restaurants_df.drop(["Country Code", "Country Id"], axis="columns")
    restaurants_df = restaurants_df[['Restaurant Id', 'Restaurant Name', 'Country', 'City', 'User Rating Votes', 'User Aggregate Rating', 'Cuisines']]

    # Convert User Aggregate Rating to float
    restaurants_df['User Aggregate Rating'] = restaurants_df['User Aggregate Rating'].astype(float)

    return restaurants_df

def get_restaurant_events (df):

    # Create an empty DataFrame for restaurant events
    restaurant_events_df = pd.DataFrame(columns=['Event Id', 'Restaurant Id', 'Restaurant Name', 'Photo URL', 'Event Title', 'Event Start Date', 'Event End Date'])

    for restaurants in df.restaurants:
        if (len(restaurants)) > 0:
            for restaurant in restaurants:
                if 'zomato_events' in restaurant['restaurant'].keys():

                    # Events
                    events = restaurant['restaurant']['zomato_events']

                    for event in events:

                        # Event Start Date
                        event_start_date = pd.to_datetime(event['event']['start_date'])
                        # Event End Date
                        event_end_date = pd.to_datetime(event['event']['end_date'])

                        if (event_start_date >= pd.to_datetime('2019-04-01')) and (event_end_date <= pd.to_datetime('2019-04-30')): 

                            # Event Id
                            event_id = event['event']['event_id']
                            # Restaurant Id
                            restaurant_id = restaurant['restaurant']['R']['res_id']
                            # Restaurant Name
                            restaurant_name = restaurant['restaurant']['name']
                            # Event Title
                            event_title = event['event']['title']
                            # Photo URL
                            if len(event['event']['photos']) > 0:
                                event_photo_urls = []
                                for photo in event['event']['photos']:
                                    event_photo_urls.append(photo['photo']['url'])
                            else:
                                event_photo_urls = "NA"

                            row = {'Event Id': event_id, 'Restaurant Id': restaurant_id, 'Restaurant Name': restaurant_name, 'Photo URL': event_photo_urls, 'Event Title': event_title, 'Event Start Date': event_start_date, 'Event End Date': event_end_date}
                            restaurant_events_df = pd.concat([restaurant_events_df, pd.DataFrame([row])], ignore_index=True)

    return restaurant_events_df

def get_rating_thresholds (df):

    # Create a new DataFrame for user ratings
    user_ratings = pd.DataFrame(columns=['rating_text', 'min_aggregate_rating', 'max_aggregate_rating'])

    for restaurants in df.restaurants:
        if len(restaurants) > 0:
            for restaurant in restaurants:
                rating_text = restaurant['restaurant']['user_rating']['rating_text']
                aggregate_rating = restaurant['restaurant']['user_rating']['aggregate_rating']
                if rating_text in ('Excellent', 'Very Good', 'Good', 'Average', 'Poor'):
                    row = {
                        'rating_text': rating_text,
                        'min_aggregate_rating': aggregate_rating,
                        'max_aggregate_rating': aggregate_rating
                    }
                    existing_row = user_ratings[user_ratings['rating_text'] == rating_text]

                    if not existing_row.empty:
                        # Update the existing row if necessary
                        min_rating = existing_row['min_aggregate_rating'].min()
                        max_rating = existing_row['max_aggregate_rating'].max()

                        if aggregate_rating < min_rating:
                            min_rating = aggregate_rating
                        if aggregate_rating > max_rating:
                            max_rating = aggregate_rating

                        user_ratings.loc[user_ratings['rating_text'] == rating_text, 'min_aggregate_rating'] = min_rating
                        user_ratings.loc[user_ratings['rating_text'] == rating_text, 'max_aggregate_rating'] = max_rating
                    else:
                        user_ratings = pd.concat([user_ratings, pd.DataFrame([row])], ignore_index=True)

    return user_ratings
    
def save_dataframe_to_s3(dataframe, object_key):
    # Define AWS credentials and S3 bucket information
    aws_access_key_id = 'access_key_id'
    aws_secret_access_key = 'secret_access_key'
    bucket_name = 'bucket_name'
    
    # Create an S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    # Save the DataFrame directly to S3 as a CSV file
    csv_buffer = dataframe.to_csv(index=False).encode()
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=csv_buffer)

def main(event, context):
    # Load data from the JSON file
    json_url = 'https://raw.githubusercontent.com/Papagoat/brain-assessment/main/restaurant_data.json'
    df = pd.read_json(json_url)

    # Load country codes from Excel file
    country_codes_df = pd.read_excel('Country-Code.xlsx')

    restaurants_df = get_restaurants(df, country_codes_df)
    save_dataframe_to_s3(restaurants_df, 'restaurants.csv')

    restaurant_events_df = get_restaurant_events(df)
    save_dataframe_to_s3(restaurant_events_df, 'restaurant_events.csv')

    thresholds = get_rating_thresholds(df)
    print(thresholds)

if __name__ == "__main__":
    main()
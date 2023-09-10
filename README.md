# Take-home Assignment for Data Engineer Intern

## Overview

This project is designed to process restaurant data from a JSON source and save it to CSV files. The data includes information about restaurants, restaurant events, and user ratings. It can be run locally or deployed to the AWS Lambda service.

## Assumptions and Design Decisions

- The project assumes that the source data is available in JSON format via a publicly accessible URL.
- The data processing is divided into three main functions: `get_restaurants`, `get_restaurant_events`, and `get_rating_thresholds`.
- The processed data is saved as CSV files, one for each function's output.
- AWS Lambda is used for deployment to process the data and save it to an S3 bucket.

## Running the Source Code Locally

To run the source code locally on your laptop, follow these steps:

1. Clone this repository to your local machine:

   ```shell
   git clone https://github.com/KaushikR1999/govtech-de.git

2. Install the required Python packages using pip:

   ```shell
   pip install -r requirements.txt

3. Run the main script to process and save the data locally:

 ```shell
   python3 data_processing.py
 ```

This will generate two CSV files: restaurants.csv, restaurant_events.csv, and the following rating_thresholds table.

<img width="402" alt="Screenshot 2023-09-10 at 4 12 24 PM" src="https://github.com/KaushikR1999/govtech-de/assets/58514719/c25f244b-fa6d-4ad7-aea8-3e9034a9df46">

## Design and Deployment in the Cloud

### AWS Lambda Deployment

To deploy this project to AWS Lambda and process data in the cloud, follow these steps:

1. **Create an S3 bucket to store the CSV files.**

2. **Configure AWS CLI with your access key ID and secret access key:**

   ```shell
   aws configure
   
3. Create an AWS Lambda function and configure it with the required execution role and permissions to access S3.

4. Package the project for deployment by creating a ZIP archive of the code and its dependencies:

```shell
   zip -r data_processing.zip .
```

5. Upload the ZIP archive to AWS Lambda.

6. Configure the Lambda function to trigger as required (periodically or in response to an event).

8. Test the Lambda function to ensure it processes data and saves it to the S3 bucket.

<img width="1523" alt="Screenshot 2023-09-10 at 4 12 48 PM" src="https://github.com/KaushikR1999/govtech-de/assets/58514719/94f67595-e786-4178-9e2a-1779b7f49026">

### Architecture Diagram

The architecture diagram illustrates the flow of data from the source JSON & Excel files to the Lambda function and then to the S3 bucket.

<img width="1614" alt="Screenshot 2023-09-10 at 5 14 14 PM" src="https://github.com/KaushikR1999/govtech-de/assets/58514719/820933e7-2ab0-4a14-9cc7-5ec680f7114c">

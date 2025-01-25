import json, base64, boto3, random, string
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context) -> json:
    domain = event["headers"]["origin"]
    if domain not in ["https://redirect.ghostvaibhav.com", "https://to.ghostvaibhav.com"]:
        return ""

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": domain,
        "Access-Control-Allow-Methods": "OPTIONS,PUT,POST",
        "Access-Control-Allow-Headers": "Content-Type, x-api-key",
    }

    if (event["httpMethod"] == "OPTIONS"):
        data = {
            "statusCode": 200,
            "headers": headers,
        }
        data = json.dumps(data)
        data = json.loads(data)
        return data

    elif (event["httpMethod"] == "PUT"):
        dynamodb = boto3.resource('dynamodb')

        body = json.loads(base64.b64decode(event["body"]))
        print(body)
        to = body['to']
        if (not to.startswith("http")) & (not to.startswith("https")):
            to = f"https://{to}"

        table = dynamodb.Table('URLS')

        shortcode = None
        print("Got the table and init shortcode")

        while True:
            shortcode = generate_random_shortcode()
            print(f"Testing {shortcode}")
            response = table.query(
                KeyConditionExpression=Key('shortcode').eq(shortcode)
            )
            if response['Count'] > 0:
                print(f"Collision with {shortcode}: {response['Items']} ||||| {response}")
                continue
            else:
                table.put_item(Item={'shortcode': shortcode, 'url': to})
                print(f"Stored {to} as {shortcode}")
                break

        body = {
            "from": shortcode
        }
        print(body)
        
        data = {
            "statusCode": 200,
            "body": json.dumps(body),
            "headers": headers,
        }
        data = json.dumps(data)
        data = json.loads(data)
        print(data)
        return data

    elif (event["httpMethod"] == "POST"):
        dynamodb = boto3.resource('dynamodb')

        body = json.loads(base64.b64decode(event["body"]))
        print(body)
        code = body['code']

        table = dynamodb.Table('URLS')

        response = table.query(
            KeyConditionExpression=Key('shortcode').eq(code)
        )

        body = None

        if response['Count'] > 0:
            body = {
                "redirect_to": response['Items'][0]['url']
            }

        data = {}
        
        if body is None:
            data = {
                "statusCode": 404,
                "headers": headers,
            }
        else:
            data = {
                "statusCode": 200,
                "body": json.dumps(body),
                "headers": headers,
            }
        
        data = json.dumps(data)
        data = json.loads(data)
        print(data)
        return data

def generate_random_shortcode() -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

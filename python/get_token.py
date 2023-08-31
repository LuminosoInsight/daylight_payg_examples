# Get a token for Daylight Pay As You Go
#
# You first have to sign up (for free) for Daylight on AWS Marketplace.
# https://github.com/LuminosoInsight/daylight_payg_examples
#
# During the signup process you setup a username and password which
# you can use with this script to generate a token which can be used
# in further calls to the API.
#
# This username, password and token are only valid for the Daylight PAYG
# system and cannot be used directly with Daylight.

import argparse
import getpass
import requests

payg_url = 'http://44.202.215.50/'
myobj = {'somekey': 'somevalue'}


def get_daylight_payg_token(username, password):
    print("getting token")
    req_body = {
        'email': username,
        'description': 'api token',
        'password': password
    }
    resp = requests.post(
        payg_url+"api/v5/payg/tokens", 
        json=req_body,
        headers={'user-agent': 'payg-example', 
                 'Content-Type': 'application/json'})
    return resp.text


def main():
    parser = argparse.ArgumentParser(
        description=('Create a token for the Luminoso Daylight PAYG system.')
    )

    args = parser.parse_args()

    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    resp = get_daylight_payg_token(username, password)
    print(f"resp: {resp}")


if __name__ == '__main__':
    main()

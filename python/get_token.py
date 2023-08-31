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
import paygsdk


def main():
    parser = argparse.ArgumentParser(
        description=('Create a token for the Luminoso Daylight PAYG system.')
    )

    args = parser.parse_args()

    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    client = paygsdk.LumiPaygSdk()
    resp = client.get_token(username, password)
    print(f"resp: {resp}")


if __name__ == '__main__':
    main()

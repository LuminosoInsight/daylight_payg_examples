import argparse
import os
import paygsdk


# curl -X GET -H "Authorization: Token $LUMI_PAYG_TOKEN" http://44.202.215.50:5002/api/v5/projects
def main():
    parser = argparse.ArgumentParser(
        description=('Get the list of projects.')
    )

    args = parser.parse_args()

    token = os.environ["LUMI_PAYG_TOKEN"]
    client = paygsdk.LumiPaygSdk(token=token)
    resp = client.get_projects()

    print(f"{resp}")


if __name__ == '__main__':
    main()
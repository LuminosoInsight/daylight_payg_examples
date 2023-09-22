import argparse
import os
import paygsdk


# curl -X POST -H "Authorization: Token $LUMI_PAYG_TOKEN" http://44.202.215.50:5002/api/v5/projects
def main():
    parser = argparse.ArgumentParser(
        description=('Create a new project')
    )

    parser.add_argument('project_name', help="Specify the project name")
    parser.add_argument('-l', '--language', default="en",
                        help="Specify the language. Default=en")

    parser.add_argument("-w", '--workspace_id', default=None,
                        help="Specify the workspace_id to use. Otherwise user default")
    args = parser.parse_args()

    token = os.environ["LUMI_PAYG_TOKEN"]
    client = paygsdk.LumiPaygSdk(token=token)
    resp = client.create_project(args.project_name, 
                                 args.language, 
                                 workspace_id=args.workspace_id)

    print(f"{resp}")


if __name__ == '__main__':
    main()
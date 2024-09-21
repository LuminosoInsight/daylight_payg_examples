# Luminos Daylight Pay As You Go (payg) example scripts

Daylight is a sophisticated engine which can harnesses the power of Natural Language Analysis, allowing you to understand and analyze vast volumes of text with precision. Through its advanced vectorization capabilities, Daylight leverages word embeddings to grasp the intricate relationships between concepts, paving the way for profound insights and captivating applications beyond traditional text analytics.

Daylight PAYG is tailored for those who demand flexibility without compromise. As an API-only offering, PAYG lets you pay solely for what you utilize, making it ideal for handling large datasets or integrating seamlessly with existing toolsets. Experience the unmatched prowess of this award-winning text analysis engine with virtually no entry barriers and at an affordable cost. Unleash your creativity and embark on innovative analysis ventures like never before!

Daylight PAYG can even accept audio files which are transcribed and processed with the Daylight Engine returning a full transcription as well as sentiment analysis on the transcription.

This repository includes API call examples and sample code for using the Luminoso Pay As You go SaaS offering on AWS. You must first sign up for the [free offering on AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-23lkym36c5ntk).

Once you have signed up you will create a username and password. You can then use that username and password to generate a token to use for the rest of your api calls.


### token generation

Use the following API call to generate a token.
```
curl -X POST -H "Content-Type: application/json" -d '{"email":"<user@example.com>", "description": "Better text analytics", "password":"<password>"}' https://daylight.luminoso.com/api/dashboards/payg/tokens
```

Output:
```
{"status": "success", "status_code": 200, "message": "Token Generated", "token": "xyzXYZxyzXYZ"}
```

You need to save the token from the output and use it for all your later API calls.  This will typicall be saved as an environment variable or into AWS Secrets Manager. It should NEVER be hard coded into your source programs even for initial testing.

For these examples you should save the token into an environment variable

export LUMI_TOKEN = xyzXYZxyzXYZ

Even more secure to save the token in a shell file so the token isn't lingering on your command line history

*setup.sh contents*
```
#!/bin/bash
export LUMI_TOKEN = xyzXYZxyzXYZ
```

Whenever you are ready to run your tests you simply call the setup file that creates the environment variable.

```
source setup.sh
```

# API examples

### Create a project
```
curl -X POST -H "Authorization: Token $LUMI_TOKEN" -H "Content-Type: application/json" -d '{"name":"my first project","language":"en"}' https://daylight.luminoso.com/api/dashboards/projects
```
Return example
```
{
    "workspace_id": "f76s8a6x",
    "creation_date": 1726118025.3686297,
    "creator": "name@example.com",
    "description": "",
    "document_count": 0,
    "language": "en",
    "next_build_language": "en",
    "last_metaupdate": 1726118025.3686297,
    "last_build_info": {},
    "last_successful_build_time": null,
    "name": "my first project",
    "project_id": "prmf2cz9",
    "permissions": [
        "create",
        "read",
        "write"
    ]
}
```

### Upload data to a project
Uploading data to a project is as simple as bundling each individual verbatim into a json object and sending that to the /upload endpoint as a list of objects. These are typically called 'documents'.

A payload for uplaoding a document list for upload uses the following format. There is a sample file included in this repository.
```
{
"docs" = [
    {
        "text": "this is the verbatim",
        "title": "Title of document",
        "metadata": [
            {
                "type": "string",
                "name": "metadata1",
                "value": "value 1"
            },
            {
                "type": "number",
                "name": "metadata2",
                "value": 2.1
            },
            {
                "type": "date",
                "name": "metadatadate",
                "value": 1472647011
            }
        ]
    }
]
}
```

To upload a list of documents use the following api call. This uses the included sample file.
```
curl -X POST -H "Authorization: Token $LUMI_TOKEN" --data-binary "@./sample_data/sample_docs.json" https://daylight.luminoso.com/api/dashboards/projects/<project_id>c/upload
```

### Build a project
```
# curl -X POST -H "Authorization: Token $LUMI_TOKEN"  https://daylight.luminoso.com/api/dashboards/projects/prx593sc/build
```
This section still needs formatting and testing. This document is a work in progress
```
# Get the list of projects, docs, concepts
# curl -X GET -H "Authorization: Token $LUMI_TOKEN" http://localhost:5002/api/v5/projects

# documents
# curl -X GET -H "Authorization: Token $LUMI_TOKEN" http://localhost:5002/api/v5/projects/prm8xsrc/docs
# curl -X GET -H "Authorization: Token $LUMI_TOKEN" 'http://localhost:5002/api/v5/projects/prm8xsrc/docs' -d '{"filter":[{"name":"Date","minimum":"2020-03-01T00:00:00Z","maximum":"2020-03-09T00:00:00Z"}],"fields":["doc_id"]}'

# Retrieve concepts
# equiv to: curl -X GET -H "Authorization: Token $LUMI_TOKEN" -d "{}" -H "Content-Type: application/json"  "https://daylight.luminoso.com/api/v5/projects/prm8xsrc/concepts"

# Concepts match counts
# curl -X GET -H "Authorization: Token $LUMI_TOKEN" http://localhost:5002/api/v5/projects/prm8xsrc/concepts/match_counts

# Concepts using concept selectors
# curl -X POST -H "Authorization: Token $LUMI_TOKEN" -H "Content-Type: application/json" -d '{"type": "top", "limit": 20}' http://localhost:5002/api/v5/projects/prm8xsrc/concepts
# curl -X POST -H "Authorization: Token $LUMI_TOKEN" -H "Content-Type: application/json" -d '[{"name": "State", "values": ["MA", "NH"]},{"name": "Rating", "maximum": 3}]' http://localhost:5002/api/v5/projects/prm8xsrc/concepts

# Transcribe audio into a project
# curl -X POST -H "Authorization: Token $LUMI_TOKEN" -F "file=@../testfile.wav" http://localhost:5002/api/v5/projects/xyz/transcribe
```

## Billing dimensions
|name       |units|cost|description         |
|-----------|------------|----|-------------|
|upload|10k characters|$0.019|10K bytes sent to the /upload endpoint|
|reviews|1k reviews|$0.49|Automatic review scraping|
|reddit_comment|1k reddit comments|$0.25|Automatic reddit scraping|
|audio_seconds|$0.009|per min|Audio transcription to Daylight project|
|builds|k characters|$0.0001|K bytes in the project being built. The first build of each project is free|
|sentiment_builds|k characters|$0.001|K bytes in the project being built. The first sentiment build of each project is free|
|api_calls|10k api calls|$0.001|10k api calls|
|storage|GB storage|$0.25/mo|The amount of storage used on a monthly basis. This is billed on a daily basis using the amount of storage/365 days|
|helios|10k requests|$0.05|Calls to Helios our LLM AI Assistant|

# Support
If you have any questions or need assistance, please reach us at [support@luminoso.com](support@luminoso.com).
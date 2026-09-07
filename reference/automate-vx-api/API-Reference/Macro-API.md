Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/Macro-API.htm

# Macro API

The **Macros** API is used to perform a series of batched API calls that are included in the body request.

NOTE: Refer to [API Reference](API-Reference.htm) for a list of all API calls and their body parameters (if required).

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/Macro

## Parameters

**Parameter Content Type**: Application/JSON

POST Macro Parameters

 

Name

Description

requests

**Required.** Body JSON that includes any API calls that should be issued within a comma-delimited list. Each API call must include an **api** and **body** parameter within a child node.

api

**Required.** String (body JSON) that sets the API call to be issued.

body

**Required.** String (body JSON) that sets the body parameters of the API call (if required).

Body JSON Formatting

```
{    "requests": [        {            "api": "[API call 1]",            "body": "[body parameters]"        },        {            "api": "[API call 2]",            "body": "[body parameters]"        }    ]}
```

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "{\"requests\": [{\"api\": \"[API Call 1]\", \"body\": \"[Parameters]\"}, {\"api\": \"[API Call 2]\", \"body\": \"[Parameters]\"}]}" https://[Server URL]:4443/api/Macro
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "{\"requests\": [{\"api\": \"ManualSwitchCamera\", \"body\": \"{\"address\": 2}\"}, {\"api\": \"ChangeRoomConfiguration\", \"body\": \"{\"id\": behnam}\"}]}" https://[Server URL]:4443/api/Macro
```

Request URL

```
https://[ServerURL]:4443/api/Macro
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Finished running requests",    "responses": [        {            "request_api": "[API call 1]",            "response_code": 200,            "response_body": "{\"status\":\"OK\",\"message\":\"[message]\"}"        },        {            "request_api": "[API call 2]",            "response_code": 200,            "response_body": "{\"message\":\"[message]\",\"status\":\"OK\"}"        }    ]}
```

NOTE: Each individual API call will return a success or error message within its **response\_body** parameter.

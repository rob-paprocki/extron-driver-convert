Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/GoToScenario-API.htm

# GoToScenario API

The **GoToScenario** API is used to call a scenario on the Automate VX system. The active shot will change to the scenario specified by the ID in the API call.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/GoToScenario

## Parameters

**Parameter Content Type**: Application/JSON

POST GoToScenario Parameters

 

Name

Description

id

**Required.** Integer (body JSON) that sets the corresponding scenario to be called on the Automate VX system.

Body JSON Formatting

```
{    "id": "[value]"}
```

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "{\"id\":\"[value]\"}" https://[Server URL]:4443/api/GoToScenario
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "{\"id\":\"1\"}" https://123.456.789.000:4443/api/GoToScenario
```

Request URL

```
https://[ServerURL]:4443/api/GoToScenario
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Successfully called scenario [value]",    "cameras": [        [1-8]    ]}
```

Error

```
{    "status": "Error",    "err": "Could not find scenario: [value]"}
```

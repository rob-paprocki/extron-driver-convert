Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/ScenarioStatus-API.htm

# ScenarioStatus API

The **ScenarioStatus** API is used to return the current scenario that has been called on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/ScenarioStatus

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/ScenarioStatus
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/ScenarioStatus
```

Request URL

```
https://[ServerURL]:4443/api/ScenarioStatus
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Successfully read selected scenario",    "scenario": {        "id": [value],        "name": "Home"    }}
```

Error

```
{    "status": "Error",    "err": "Failed to read selected scenario"}
```

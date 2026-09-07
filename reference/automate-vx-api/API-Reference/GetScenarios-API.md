Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/GetScenarios-API.htm

# GetScenarios API

The **GetScenarios** API is used to return the name and ID of all scenarios on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/GetScenarios

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/GetScenarios
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/GetScenarios
```

Request URL

```
https://[ServerURL]:4443/api/GetScenarios
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Scenarios loaded successfully",    "scenarios": [        {            "id": [value],            "name": "Home"        }    ]}
```

Error

```
{    "status": "Error",    "err": "Failed to read available scenarios"}
```

Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/ChangeLayout-API.htm

# ChangeLayout API

The **ChangeLayout** API is used to change the active layout on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/ChangeLayout

## Parameters

**Parameter Content Type**: Application/JSON

POST ChangeLayout Parameters

 

Name

Description

id

**Required.** String (body JSON) that sets the layout ID that the Automate VX system will change to upon issuing this API call. Valid values are A through Z.

Body JSON Formatting

```
{    "id": "[value]"}
```

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "{\"id\":\"[value]\"}" https://[Server URL]:4443/api/ChangeLayout
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "{\"id\":\"H\"}" https://123.456.789.000:4443/api/ChangeLayout
```

Request URL

```
https://[ServerURL]:4443/api/ChangeLayout
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Changed to Layout [A-Z]"}OR{    "status": "OK",    "message": "Already on Layout [A-Z]"}
```

Error

```
{    "status": "Error",    "err": "[Reason for error]"}
```

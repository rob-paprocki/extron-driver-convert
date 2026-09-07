Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/GoHome-API.htm

# GoHome API

The **GoHome** API is used to switch to the home shot preset on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/GoHome

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/GoHome
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/GoHome
```

Request URL

```
https://[ServerURL]:4443/api/GoHome
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Successfully called Home Shot and preset"}
```

Error

```
{    "status": "Error",    "err": "[Reason for error]"}
```

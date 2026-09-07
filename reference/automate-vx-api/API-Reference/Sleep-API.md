Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/Sleep-API.htm

# Sleep API

The **Sleep** API is used to turn off all Automate VX system functions and calls a camera preset for all cameras.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/Sleep

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/Sleep
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/Sleep
```

Request URL

```
https://[ServerURL]:4443/api/Sleep
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "VX went to sleep successfully"}
```

Error

```
{    "status": "Error",    "err": "[Reason for error]"}
```

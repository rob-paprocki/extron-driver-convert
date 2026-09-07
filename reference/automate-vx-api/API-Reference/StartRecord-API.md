Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StartRecord-API.htm

# StartRecord API

The **StartRecord** API is used to start recording on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/StartRecord

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/StartRecord
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/StartRecord
```

Request URL

```
https://[ServerURL]:4443/api/StartRecord
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Record Started Successfully"}
```

Error

```
{    "status": "Error",    "err": "Failed to Start Recording"}
```

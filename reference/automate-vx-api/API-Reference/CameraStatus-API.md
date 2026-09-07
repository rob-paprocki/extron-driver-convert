Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/CameraStatus-API.htm

# CameraStatus API

The **CameraStatus** API is used to retrieve the status of the active camera shot on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/CameraStatus

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/CameraStatus
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/CameraStatus
```

Request URL

```
https://[ServerURL]:4443/api/CameraStatus
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Live camera address queried successfully",    "address": "[value]"}
```

Error

```
{    "status": "Error",    "err": "[Reason for error]"}
```

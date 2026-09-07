Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/ShotStatus-API.htm

# ShotStatus API

The **ShotStatus** API is used to return the camera or scenario that is currently active. The layout and previous layout (for side-by-side shots) are also provided.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/ShotStatus

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/ShotStatus
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/ShotStatus
```

Request URL

```
https://[ServerURL]:4443/api/ShotStatus
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Shot status queried successfully.",    "shotname": -1,    "layout": "A",    "storedLayout": "A",    "cam1": 1,    "cam2": -1}
```

Error

```
{    "status": "Error",    "err": "[Reason for error]"}
```

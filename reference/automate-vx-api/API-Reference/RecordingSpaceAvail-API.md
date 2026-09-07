Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/RecordingSpaceAvail-API.htm

# RecordingSpaceAvail API

The **RecordingSpaceAvail** API is used to retrieve how much recording space is available (in GB) on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/RecordingSpaceAvail

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/RecordingSpaceAvail
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/RecordingSpaceAvail
```

Request URL

```
https://[ServerURL]:4443/api/RecordingSpaceAvail
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Available recording storage queried successfully",    "available_gigabytes": "[value]",    "total_gigabytes": "[value]"}
```

Error

```
{    "status": "Error",    "err": "[Reason for error]"}
```

NOTE: Available recording space that is returned will be rounded down to the nearest gigabyte.

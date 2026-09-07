Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StreamStatus-API.htm

# StreamStatus API

The **StreamStatus** API is used to obtain the status of streaming on the Automate VX system.

NOTE: Stream settings must be configured on the Automate VX system before the **StreamStatus** API will function. For more information, refer to the [IV‑SAM‑VXP‑1B and IV‑SAM‑VSX‑1B Product Manual](https://docs.crestron.com/en-us/9324/Content/Topics/Home.htm).

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/StreamStatus

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/StreamStatus
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/StreamStatus
```

Request URL

```
https://[ServerURL]:4443/api/StreamStatus
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "results": true,    "message": "Stream in Progress"}OR{    "status": "OK",    "results": false,    "message": "No Stream in Progress"}
```

Error

```
{    "status": "Error",    "err": "Failed to Fetch Stream Status"}
```

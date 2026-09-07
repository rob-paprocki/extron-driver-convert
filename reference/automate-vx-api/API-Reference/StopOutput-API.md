Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StopOutput-API.htm

# StopOutput API

The **StopOutput** API is used to stop live output over a configured interface on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/StopOutput

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/StopOutput
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/StopOutput
```

Request URL

```
https://[ServerURL]:4443/api/StopOutput
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Output Stopped"}OR{    "status": "OK",    "message": "No output in progress"}
```

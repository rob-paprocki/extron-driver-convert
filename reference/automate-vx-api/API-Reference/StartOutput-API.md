Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StartOutput-API.htm

# StartOutput API

The **StartOutput** API is used to start live output over a configured interface on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/StartOutput

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/StartOutput
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/StartOutput
```

Request URL

```
https://[ServerURL]:4443/api/StartOutput
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Started Output"}OR{    "status": "OK",    "message": "Output is in progress"}
```

Error

```
{    "status": "Error",    "err": "Output is disabled"}
```

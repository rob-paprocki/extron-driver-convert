Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/Restart-API.htm

# Restart API

The **Restart** API is used to restart the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/Restart

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/Restart
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/Restart
```

Request URL

```
https://[ServerURL]:4443/api/Restart
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Restart command initiated"}
```

Error

```
{    "status": "Error",    "err": "Could not restart. [Reason for error]"}
```

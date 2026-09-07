Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/GetCameras-API.htm

# GetCameras API

The **GetCameras** API is used to retrieve all configured camera models in the current room configuration.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/GetCameras

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/GetCameras
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/GetCameras
```

Request URL

```
https://[ServerURL]:4443/api/GetCameras
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "cameras loaded successfully",    "cameras": [        {            "id": "[value]",            "name": "[model name]",            "ip": "[ip address]"        }    ]}
```

Error

```
{    "status": "Error",    "err": "[Reason for error]"}
```

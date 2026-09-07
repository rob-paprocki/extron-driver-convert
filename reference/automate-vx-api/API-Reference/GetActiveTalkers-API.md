Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/GetActiveTalkers-API.htm

# GetActiveTalkers API

The **GetActiveTalkers** API is used to retrieve the virtual microphone position that is reporting an active speaking participant. A second virtual microphone position is returned if conversation mode or a side-by-side shot is actively being used.

NOTE: "defaultshot": 1 is returned if the default camera shot is active. "defaultshot": 0 is returned if the default camera shot is not active.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/GetActiveTalkers

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/GetActiveTalkers
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/GetActiveTalkers
```

Request URL

```
https://[ServerURL]:4443/api/GetActiveTalkers
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "talkers": "[5,]",    "defaultShot": 0}
```

OR

```
{    "status": "OK",    "talkers": "[5,8]",    "defaultShot": 0}
```

OR

```
{    "status": "OK",    "talkers": "[ ]",    "defaultShot": 1}
```

Error

```
{    "status": "Error",    "err": "[Reason for error]"}
```

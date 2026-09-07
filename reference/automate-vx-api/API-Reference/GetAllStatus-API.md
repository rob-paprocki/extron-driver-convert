Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/GetAllStatus-API.htm

# GetAllStatus API

The **GetAllStatus** API is used to return the status of all available Automate VX functions (such as switching, recording, streaming, and layout) within a single API call.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/GetAllStatus

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/GetAllStatus
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/GetAllStatus
```

Request URL

```
https://[ServerURL]:4443/api/GetAllStatus
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "api_call_0": {        "request_api": "AutoSwitchStatus",        "response_code": 200,        "response_body": "{\"message\":\"No AutoSwitching in Progress\",\"results\":false,\"status\":\"OK\"}"    },    "api_call_1": {        "request_api": "StreamStatus",        "response_code": 200,        "response_body": "{\"status\":\"OK\",\"results\":false,\"message\":\"Streaming not in progress\"}"    },    "api_call_2": {        "request_api": "OutputStatus",        "response_code": 200,        "response_body": "{\"status\":\"OK\",\"results\":true,\"message\":\"Outputting in progress\"}"    },    "api_call_3": {        "request_api": "ISORecordStatus",        "response_code": 200,        "response_body": "{\"status\":\"OK\",\"results\":false,\"message\":\"Recording ISO not in progress\"}"    },    "api_call_4": {        "request_api": "RecordStatus",        "response_code": 200,        "response_body": "{\"status\":\"OK\",\"results\":false,\"message\":\"Recording not in progress\"}"    },    "api_call_5": {        "request_api": "RecordingSpaceAvail",        "response_code": 200,        "response_body": "{\"status\":\"OK\",\"message\":\"Available recording space queried successfully.\",\"available_gigabytes\":207,\"total_gigabytes\":232}"    },    "api_call_6": {        "request_api": "CopyStatus",        "response_code": 200,        "response_body": "{\"status\":\"OK\",\"message\":\"Not copying.\",\"copy_underway\":false}"    },    "api_call_7": {        "request_api": "GetCameras",        "response_code": 200,        "response_body": "{\"status\":\"OK\",\"message\":\"cameras loaded successfully\",\"cameras\":[{\"id\":1,\"model\":\"ip20\"},{\"id\":2,\"model\":\"ip20\"}]}"    },    "api_call_8": {        "request_api": "CameraStatus",        "response_code": 200,        "response_body": "{\"status\":\"OK\",\"message\":\"Live camera address queried successfully.\",\"address\":1,\"addresses\":[1]}"    },    "api_call_9": {        "request_api": "GetLayouts",        "response_code": 200,        "response_body": "{\"status\":\"OK\",\"message\":\"Layouts loaded successfully\",\"layouts\":[{\"id\":\"A\",\"name\":\"Layout A\"},{\"id\":\"B\",\"name\":\"Layout B\"}]}"    },    "api_call_10": {        "request_api": "LayoutStatus",        "response_code": 200,        "response_body": "{\"status\":\"OK\",\"message\":\"Current layout queried successfully\",\"layout\":{\"id\":\"A\",\"name\":\"Layout A\"}}"    },    "api_call_11": {        "request_api": "GetRoomConfigs",        "response_code": 200,        "response_body": "{\"status\":\"OK\",\"message\":\"Room configs loaded successfully\",\"roomConfigs\":[{\"id\":1,\"name\":\"Config 1\"},{\"id\":2,\"name\":\"Config 2\"}]}"    },    "api_call_12": {        "request_api": "RoomConfigStatus",        "response_code": 200,        "response_body": "{\"status\":\"OK\",\"message\":\"Current room configuration queried successfully\",\"roomConfig\":{\"id\":1,\"name\":\"Config 1\"}}"    }}
```

NOTE: Each individual response code is of type number. Each individual response body is of type string and must be deserialized by the client.

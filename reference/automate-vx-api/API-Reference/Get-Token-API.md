Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/Get-Token-API.htm

# Get-Token API

The **Get-Token** API is used to obtain an authentication token from the Automate VX server that must be used to authenticate all other API call requests.

**NOTE:** An "Authorization" header must be appended to this request with a value of "YWRtaW46MWJleW9uZA==", which is the default Automate VX username and password (**admin:1beyond**) encoded into base64 format. If the default username and password has been changed, you must encode the new username and password (formatted as "username:password") into base64 format for use within the "Authorization" header. A free encoding tool is available at [www.base64encode.org](https://www.base64encode.org/).

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /get-token

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Encoded Username and Password]" -X POST --data "" https://[Server URL]:4443/get-token
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: YWRtaW46MWJleW9uZA==" -X POST --data "" https://123.456.789.000:4443/get-token
```

Request URL

```
https://[ServerURL]:4443/get-token
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "token": [token],}
```

Error

```
{    "status": "Error",    "err": "Incorrect Username or Password"}
```

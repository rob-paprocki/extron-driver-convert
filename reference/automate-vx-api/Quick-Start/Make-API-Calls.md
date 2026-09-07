Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/Quick-Start/Make-API-Calls.htm

# Make API Calls

To make API calls to the Automate VX server:

1.  Obtain a valid authentication token from the Automate VX server as described in [Authentication](Authentication.htm).
2.  Open an API development environment program (such as [Postman](https://www.postman.com/)) that supports HTTP requests.
3.  Issue an HTTP request that includes the required HTTP method, headers, and parameters for the desired API call as described in [API Reference](../API-Reference/API-Reference.htm). The authentication token obtained in step 1 must be appended to the request in an "Authorization" header.

If accessing the API layer via cURL, the cURL command must be formatted as follows, with any parameters entered after the authorization token in the appropriate format (application/json):

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" http://[Server URL]:4443/api/[APIDirectory]
```

The format of the cURL command can also be used to make web calls in other programming languages.

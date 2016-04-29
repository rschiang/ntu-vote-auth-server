## API requirements
General requirements:  

- version (the api version)
- api_key (the api key)

### register
- username
- password

### ping
GET
- token (in the header)

### status
GET
- token (in the header)

### authenticate
- token (in the header)
- cid
- uid

### confirm
- token (in the header)
- uid
- auth_token

### report
- token (in the header)
- uid

### complete
nothing but a callback api

### reset
TBD
- token (in the header)

### migration
TBD
- token (in the header)


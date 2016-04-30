# Voteing API version 2
## API requirements
General requirements:  

- version (the api version)
- api_key (the api key)

### register
- username
- password

### ping
GET
- token

### status
GET
- token

### authenticate
- token
- cid
- uid

### confirm
- token
- uid
- vote_token

### report
- token
- uid

### complete
nothing but a callback api

### reset
TBD
- token

### migration
TBD
- token


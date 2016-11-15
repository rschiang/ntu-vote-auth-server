# Voteing API version 2
Each 
#####request
 cotains a json object with specified column.
## API Argument
General argument, all API call should cotains following arguments: 

- version (the api version)
- api_key (the api key)

## register
POST
#####Request

- username
- password

#####Response

- status
- name
- station_id
- token

## ping
GET

#####Request

- token

#####Response

- status
- timestamp

## status
GET

#####Request


- token

#####Response


- status
- ballot
 - used
 - remain
- stations(:array)
 - name
 - id 
 - status

## authenticate
POST

#####Request

- token
- cid
- uid

#####Response

- status
- uid
- type
- vote_token

## confirm
POST

#####Request

- token
- uid
- vote_token

#####Response

- status
- ballot
- callback

## report
POST
#####Request

- token
- uid

#####Response

- status

## complete
GET  
nothing but a callback api.
Require a GET argument `callback`.

#####Response

- status
- message

## reset
TBD

- token

## migration
TBD

- token


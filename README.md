<img src="./.github/ruby-banner.png">

# Ruby API
Welcome to the Ruby API! Learn how to use weight data from Ruby in your projects.

# Authentication
The Ruby server uses basic HTTP authentication. Since the only version of Ruby currently available is on Discord, users’
username is their Discord user id. The bot provides their passcode. Your program will not get user weight data without the user id and the passcode.

### Errors

|Error Message|Suggestion|
|---|---|
|Wrong passcode.|Ensure that the passcode is the passcode associated with the user id.|
# Messages and Errors
Every JSON response will include a `message` key that will be either “SUCCESS” or “ERROR: ” followed by the error 
message. It is suggested that you inspect the `message` value for either “SUCCESS” or “ERROR”.

# Documentation
## `GET` /api/weight/MONTH_REQUESTED/
Returns weight data of a user.

### Example response:
```json
{
  "weight": {
    "2021-12-05": 197.0,
    "2021-12-10": 197.0
  },
  "message": "SUCCESS"
}
```

### Errors

|Error Message|Suggestion|
|-----|-----|
|User `user_id` is not in the database.| The user does not exist. Try creating it using `/api/new-user/` and try again. |
|Requested month is in wrong format. Must be in format xxxx-xx (YEAR-MONTH).|The `MONTH_REQUESTED` part of the link must be either "-" for the current month or the format requested by the error.|

## `POST` /api/update-weight/
Updates an individual’s weight data and returns weight data similar to `/api/weight/-/`.
<br>
Your program must provide JSON data to use this URL.

### Example request:
```json
{
  "user_id": "Carlos",
  "weight": "190"
}
```

### Example response:
```json
{
  "weight": {
    "2021-12-05": 197.0,
    "2021-12-10": 197.0
  },
  "message": "SUCCESS"
}
```

### Errors

|Error Message|Suggestion|
|-----|-----|
|'user_id' must be included.|The JSON data must include `user_id`.|
|'weight' must be included.|The JSON data must include `weight`.|
|`EXTRA KEY` is unrecognized. Please remove it.|You cannot include extra keys. Only `user_id` and `weight` are allowed.|

## `POST` /api/new-user/
Creates a new user.<br>
Your program must provide JSON data to use this URL.

### Example request:
```json
{
  "user_id": "create a user id",
  "passcode": "create a passcode"
}
```

### Errors

|Error|Description|
|-----|------|
|User `user_id` already exists.|This user id is taken. Use another one.|
|'user_id' must be included.|The JSON data must include `user_id`.|
|'passcode' must be included.|The JSON data must include `passcode`.|
|`EXTRA KEY` is unrecognized. Please remove it.|You cannot include extra keys. Only `user_id` and `passcode` are allowed.|
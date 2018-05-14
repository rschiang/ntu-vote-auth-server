# 電子投票身份驗證系統
## 簡介
- 為辦理台大學生會所舉辦之學生自治投票，本系統為身份驗證子系統，只提供學生證的查詢、認證、電子選票之派發。

- Version 3.0
- Based on Python 3.5

## 相依套件
- Django: 1.9.5
- djangorestframework: 3.3.3
- gunicorn: 19.3.0

## 角色
- Station: 投票站
- Admin:  管理員
- Supervisor: 監察員
- Voting System: 計票子系統

## 需求描述
|編號 |            需求描述    | A |Sup|Stn|
|-----|------------------------|---|---|---|
| G01 | 認證工作人員身分       | v | v | v |
| G02 | Heartbeat              | v | v | v |
| A01 | 驗證學生證             |   |   | v |
| A02 | 確認選舉人並派發選票   |   |   | v |
| A03 | 否決選舉人             |   |   | v |
| A04 | 確認選票抵達(公開端點) |   |   |   |
| R01 | 列出重設選舉人請求     | v | v |   |
| R02 | 申請重設選舉人狀態     | v |   |   |
| R03 | 確認重設選舉人狀態     |   | v |   |
| R04 | 駁回重設選舉人狀態     |   | v |   |
| C01 | 新增 Entry 對應        |   | v |   |
| C02 | 修改 Entry 對應        |   | v |   |
| C03 | 刪除 Entry 對應        |   | v |   |
| C04 | 列出 Entry 對應        |   | v |   |
| C05 | 設定投票時間           |   | v |   |
| C06 | 下載選票檔案           |   | v |   |
| T01 | 測試教務處系統         |   | v |   |
| T02 | 測試計票子系統         |   | v |   |
| T03 | 本系統獨立測試         |   |   |   |
| M01 | 選票狀態               | v | v |   |
| M02 | 票站狀態               | v | v |   |

## 模組

- Record
- AuthCode
- AuthToken
- Entry
- OverrideEntry
- User
- Station

## 資源

| 名稱       | 說明              |
|------------|-------------------|
| `general`  | 工作人員身份認證  |
| `elector`  | 選舉人相關        |
| `entry`    | 身份對應表        |
| `reset`    | 重設選舉人狀態    |
| `test`     | 測試              |
| `status`   | 系統狀態          |

# API
#### 通用參數

- version (the api version)
- api_key (the api key)

#### HTTP Request Example
```json
{
    "version": 3,
    "api_key": "test_api_key",
    "username": "MY_USER_NAME",
    "password": "MY_SUPER_SECRET_PASSWORK"
}
```

#### 通用錯誤訊息格式
```json
    {
        "status": "error",
        "message": "<string:message>"
    }
```
#### 通用錯誤訊息
- params_invalid
- version_not_supported
- token_required
- unauthorized
- session_expired
- permission_denied
- station_error
- service_closed

#### API 清單

| 名稱                   | URL                     |
|------------------------|-------------------------|
| Register               | /general/login          |
| Ping                   | /general/login          |
| Status                 | /status                 |
| Authenticate           | /elector/authenticate   |
| Confirm                | /elector/confirm        |
| Report                 | /elector/report         |
| Callback               | /elector/complete       |
| List Reset Request     | /resets/                |
| Apply Reset Request    | /resets/apply           |
| Confirm Reset Request  | /resets/confirm         |
| Reject Reset Reques    | /resets/reject          |
| List Entry             | /entry/                 |
| Create Entry           | /entry/                 |
| Retrieve Entry         | /entry/:dpt_code        |
| Update Entry           | /entry/:dpt_code        |
| Delete Entry           | /entry/:dpt_code        |

### Register
- `G01`

#### url 
`POST /general/login`

#### argument
- username
- password

#### success response
- Code: `200`
```json
{
    "status": "success",
    "name": "<string>",
    "station_id": "<int>",
    "token": "<string>"
}
```

#### error response
- Code: 401
 - unauthorized

### Ping
- `G02`

#### url
`/general/login`

#### argument
- token

#### success response
- Code: 200
```json
    {
        "status": "success",
        "timestamp": "<string:isoformat>"
    }
```

#### error response
None

### Status
- `M01`
- `M02`

#### url
`/status`
#### argument
- token

#### success response
- Code: 200
```json
    {
        "status": "success",
            "ballot": {
                "used": "<int>",
                "remain": "<int>"
            },
            "stations": [{
                "name": "<string>",
                "id": "<int>",
                "status": "<string:isoformat>"
            }]
    }
```

#### error response
None

### Authenticate
- `A01`

#### url
`/elector/authenticate`
#### argument
- token
- cid
- uid

#### success response
- Code: 200
```json
{
    "status": "success",
    "uid": "<string:student_id>",
    "type": "<string>",
    "college": "<string>",
    "vote_token": "<string>"
}
```

#### error response
- card_invalid
- external_error
- card_suspicious
- duplicate_entry
- entry_not_found
- unqualified

### Confirm
- `A02`

#### url
`/elector/confirm`
#### argument
- token
- uid
- vote_token

#### success response
- Code: 200
```json
{
    "status": "success",
    "ballot": "<string>",
    "callback": "<string:url>"
}
```

#### error response
- out_of__authcode (status: `503`)
- token_invalid

### Report
- `A03`

#### url
`/elector/report`
#### argument
- token
- uid

#### success response
- Code: 200
```json
{
    "status": "success"
}
```

#### error response
- token_invalid

### Complete
- `A04`

#### url
`GET /elector/complete`
#### argument
- callback
#### success response
- Code: 200
```json
{
    "status": "success",
    "message": "all correct"
}
```

#### error response
None

### List Reset Request
- `R01`
#### url
`GET /resets/`
#### argument
- token

#### success response
- Code: 200
```json
{
    "status": "success",
    "target": [
        {
            "student_id": "<string>"
        }
    ]
}
```

### Apply Reset Request
- `R02`
#### url
`POST /resets/apply`
#### argument
- uid
- token

#### success response
- Code: 200
```json
{
    "status": "success",
    "message": "reset request created"
}
```

#### error response
- student_not_found

### Confirm Reset Request
- `R03`

#### url
`GET /resets/confirm`
#### argument
- uid
- token

#### success response
- Code: 200
```json
{
    "status": "success",
    "message": "reset request confirmed"
}
```

#### error response
- student_not_found
- reset_request_not_found

### Reject Reset Request
- `R04`
#### url
`GET /resets/reject`
#### argument
- uid
- token

#### success response
- Code: 200
```json
{
    "status": "success",
    "message": "reset request rejected"
}
```

#### error response
- student_not_found

### List Entry
- `C05`
#### url
- `GET /entry/`

#### argument
- token

#### success response
- Code: 200
```
{
    "status": "success",
    "entrys": [
        {
            "dpt_code": "<string>",
            "name": "<string>",
            "kind": "<string>",
        }
    ]
}
```

#### error response
None

### Add Entry
- `C01`

#### url
- `POST /entry/`

#### argument
- token
- name
- dpt_code
- kind

#### success response
- Code: 200
```
{
    "status": "success",
    "entry": {
        "name": "<string>",
        "dpt_code": "<string>",
        "kind": "<string>",
    }
}
```

#### error response
None


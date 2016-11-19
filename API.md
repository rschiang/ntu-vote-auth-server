# 電子投票身份驗證系統
## 簡介
- 為辦理台大學生會所舉辦之學生自治投票，本系統為身份驗證子系統，只提供學生證的查詢、認證、電子選票之派發。

- Version 3.0
- Based on Python

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
| R01 | 申請重設選舉人狀態     | v |   |   |
| R02 | 確認重設選舉人狀態     |   | v |   |
| R03 | 駁回重設選舉人狀態     |   | v |   |
| C01 | 新增 Entry 對應        |   | v |   |
| C02 | 修改 Entry 對應        |   | v |   |
| C03 | 更新 Entry 對應        |   | v |   |
| C04 | 刪除 Entry 對應        |   | v |   |
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
| `voter`    | 選舉人相關        |
| `entry`    | 身份對應表        |
| `reset`    | 重設選舉人狀態    |
| `test`     | 測試              |
| `status`   | 系統狀態          |

# API
#### 通用參數

- version (the api version)
- api_key (the api key)

#### 通用錯誤訊息格式
```
    {
        "status": "error",
        "message": <string:message>
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

### Register
- G01

#### url 
`POST /general/login`

#### argument
- username
- password

#### success response
- Code: 200
```
{
    "status": "success",
    "name": <string>,
    "station_id": <int>,
    "token": <string>
}
```

#### error response
- Code: 401
 - unauthorized

### Ping
- G02

#### url
`/general/login`

#### argument
- token

#### success response
- Code: 200
```
    {
        "status": "success",
        "timestamp": <string:isoformat>
    }
```

#### error response
None

### Status
- M01
- M02

#### url
`/status`
#### argument
- token

#### success response
- Code: 200
```
    {
        "status": "success",
            "ballot": {
                "used": <int>,
                "remain": <int>
            },
            "stations": [{
                "name": <string>,
                "id": <int>,
                "status": <string: isoformat>
            }]
    }
```

#### error response
None

### Authenticate
- A01

#### url
`/voter/authenticate`
#### argument
- token
- cid
- uid

#### success response
- Code: 200
```
{
    "status": "success",
    "uid": <string:student_id>,
    "type": <string>, 
    "college": <string>,
    "vote_token": <string>
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
- A02

#### url
`/voter/confirm`
#### argument
- token
- uid
- vote_token

#### success response
- Code: 200
```
{
    "status": "success",
    "ballot": <string>,
    "callback": <string:url>
}
```

#### error response
- out_of__authcode (status: `503`)
- token_invalid

### Report
- A03

#### url
`/voter/login`
#### argument
- token
- uid

#### success response
- Code: 200
```
{
    "status": "success"
}
```

#### error response
- token_invalid

### Callback
- A04

#### url
`/general/callback`
#### argument
#### success response
- Code: 200
```
{
    "status": "success",
    "message": "all correct"
}
```

#### error response
None

### Reset Application
- R01

### Reset Application
- R02

### Reset Application
- R03

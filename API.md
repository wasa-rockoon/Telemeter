# REST API


# 機体構成


## GET /systems

機体構成一覧を取得

## GET /systems/{system_id}

機体構成を取得


## POST /systems

機体構成を作成


# 運用

## GET /systems/{system_id}/operations

運用一覧を取得

## POST /systems/{system_id}/operations

新規運用を作成

## GET /operations/{operation_id}

運用の詳細

## GET /operations/{operation_id}/close

運用を終了


# パケット

## GET /operations/{operation_id}/packets

### Parameter

| parameter | type   | info                                   |
| ----      | ----   | ----                                   |
| count     | int    | 最大数                                 |
| cursor    | int    | カーソル                               |
| time      | string | 時刻                                   |
| retro     | bool   | カーソルまたは時刻から過去方向に進むか |
| skip      | int    | 指定した数飛ばしで取得                 |
| types     | string | パケットタイプ                         |
| sample    | int | サンプリング時間（ミリ秒)                |

### Returns

| field   | type   | info     |
| ----    | ----   | ----     |
| count   | int    | 数       |
| packets | array  | パケット |
| next    | int    | 続きのカーソル  |

## WebSocket /{system_id}/

アクティブな運用に対するソケット

## WebSocket /{system_id}/operations/{operation_id}

指定した運用に対するソケット

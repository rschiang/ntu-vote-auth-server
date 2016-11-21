NTUVote 身分驗證系統
===================

![TravisCI](https://travis-ci.org/azdkj532/ntu-vote-auth-server.svg?branch=master)

這是用於電子投票的身分驗證系統伺服器，將在臺灣大學 103 學年度第一學期學代會學生代表選舉使用。系統架構以 Django REST Framework 為基礎，藉由讀取卡片資訊、並與校務系統連線，使得此次電子投票得以透過自動化的方式驗證身分、派發選票，並有效過濾偽卡。

完整電子投票系統架構分為驗證與投票兩部分，其中裝置整合與身分驗證系統由[臺灣大學學生會選舉罷免執行委員會](https://www.facebook.com/NTUVote)委託[臺灣大學開源社](https://ntuosc.org) [RSChiang](https://github.com/rschiang/ntu-vote-auth-server) 規劃研發；投票系統則延請 [MouseMs](https://github.com/mousems/NTUvoteV2) 實作。

此專案以 [Apache 2.0](LICENSE.md) 授權釋出供公眾使用。

系統需求 / System Requirements
-----------------------------

身分驗證系統使用下列環境建置：

* Ubuntu 14.04
* Python 3.4
* PostgreSQL 9.3

專案依賴的套件與版本可參考 `requirements.txt`，所需設定的環境變數可以在 `core/settings.py` 找到。

安裝 / Install
--------------
    git clone https://github.com/rschiang/ntu-vote-auth-server
    pip install virtualenv

    # (a) For environment with Python 2.7 as default
    apt-get install python3
    virtualenv --python=`which python3` venv

    # (b) For enviroment with newer Python installation
    virtualenv venv

    # Install dependencies
    source venv/bin/activate
    pip install -r requirements.txt

    # Additional dependencies for PostgreSQL
    sudo apt-get install libpq-dev
    pip install psycopg2

    # Forking configuration file and export its path
    cp examples/settings.json settings.json
    export SETTINGS_FILE=`readlink -f settings.json`

    # Create tables
    ./manage.py migrate

    # Running dev server on localhost:8000
    ./manage.py runserver

    # Use Gunicorn when you're ready
    # You might want to bind to unix socket (e.g. "unix:/tmp/gunicorn.sock")
    # and use Nginx to serve static files instead.
    gunicorn core.wsgi --bind=0.0.0.0:80


NTU Vote Authentication Server
------------------------------

This project is the authentication server that will be used in the upcoming 103-1 NTU Student Council Representative Election. Based on Django REST Framework, the authentication system enables the automation of identity verification process, while significantly reduces the chance for electoral fraud.

The full e-vote architecture consists of two distinguish parts: authentication and ballot-casting. The authentication and device integration part is done by [NTU Open Source Community](https://ntuosc.org) under the delegation of [NTU Students' Association Election Commission](https://www.facebook.com/NTUVote), while [MouseMs](https://github.com/mousems/NTUvoteV2) from NTUST is in charge of the voting system.

This project is released under [Apache License 2.0](LICENSE.md).

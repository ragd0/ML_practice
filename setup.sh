#!/bin/bash
apt-get update		# ubuntuのパッケージデータベースをアップデート(dockerコンテナは初期状態ではデータベースが空っぽ)
apt-get install -y time	# 実行時間測定用パッケージをインストール
pip install -r requirements.txt
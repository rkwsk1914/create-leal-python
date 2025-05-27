# 手順

## 1. venv起動
```
source venv/bin/activate
```

## 2. zipファイルの作成
```
zip -r create-leal.zip . -x "venv/*" ".git/*" "dist/*" "check/*"
```

## 3. チャットGPTに流す
zipファイルとテキストを流して、JSONファイルの中身を生成


## 4. コマンド実行
チェック
```
check_display.py json/leal-{number}.json
```
本番
```
index.py json/leal-{number}.json dist/leal-{number}.mp4
```
# eventpix-api

API server for Eventpix

## 起動方法

```bash
$ docker compose up --build
```

## デプロイのテスト方法

1. `.secrets.example` をコピーして `.secrets` を作成する
2. `.secrets` にシークレット変数を設定する
3. 以下のコマンドを実行する

```bash
$ act -W .github/workflows/deploy.yml --secret-file .secrets
```

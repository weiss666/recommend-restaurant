# RUNBOOK

## 本地启动

1. `pip install -r requirements.txt`
2. `copy .env.example .env` (Windows) 或 `cp .env.example .env`
3. `python -m uvicorn app.main:app --reload`
4. 打开 `http://127.0.0.1:8000/`

## 首次无数据怎么办

- 启动时会自动写入示例数据；
- 也可手动触发：
  - `POST /api/collect?city=上海&date_from=2025-09-06&date_to=2026-03-06`

## 常见问题

- 定位失败：浏览器拒绝了定位权限，使用手动输入框填 `lat,lng`
- 距离显示为 `-`：餐厅缺经纬度或未设置当前位置
- 数据太少：调整 `min_rating` 或补充采集数据源配置

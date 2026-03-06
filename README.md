# Recommend Restaurant

一个可复用的“高分餐厅采集 + 筛选展示”项目，默认展示上海高分餐厅，支持定位授权与手动修改当前位置并显示距离。

## 功能

- 合规采集入口（聚合 API，可配置时间窗口）
- 默认近半年窗口：`2025-09-06 ~ 2026-03-06`
- 筛选字段：
  - 城市、区、热门地点、人均、标签、店名、推荐菜、来源、是否宠物友好、最近商区
- 前端定位：
  - 浏览器授权定位
  - 手动输入位置（`lat,lng` 或预置地点名）
- 结果显示距离（km）

## 快速开始

```bash
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

打开 `http://127.0.0.1:8000/`

## 采集命令

```bash
python scripts/fetch_restaurants.py --city 上海 --from 2025-09-06 --to 2026-03-06 --min-rating 4.5
```

说明：
- 若未配置 `AGGREGATOR_API_KEY`，会自动使用内置示例数据（保证页面可直接跑起来）。
- 配置 API Key 后，会调用 `AGGREGATOR_BASE_URL` 进行真实采集。

## API

- `GET /health`
- `GET /api/filter-options`
- `GET /api/restaurants`
- `GET /api/location/resolve?q=静安寺` 或 `q=31.2304,121.4737`
- `POST /api/collect?city=上海&date_from=2025-09-06&date_to=2026-03-06&min_rating=4.5`

## 可复用扩展建议

- 新增数据源：实现 `app/collectors/base.py` 接口
- 增加排序策略：在 `app/services/query_service.py` 扩展排序参数
- 接入前端框架：保留 API 不变，替换 `web/` 即可

# 合规高分餐厅采集与筛选页面

**Goal:** 用户打开页面后默认看到上海高分餐厅；顶部固定下拉筛选；支持定位授权与手动修改当前位置，并显示到店距离。  
**Solution:** 采用 `FastAPI + SQLite + 静态 HTML/JS` 架构，后端提供可复用数据采集与查询 API，前端实现固定筛选条、列表渲染、定位授权与位置输入。数据采集采用合规聚合 API（近半年窗口：2025-09-06 ~ 2026-03-06），入库后统一清洗并支持增量更新。  
**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, SQLite, httpx, pydantic, vanilla HTML/CSS/JS

---

## Non-Goals (What we won't do)
- 不做绕过反爬/风控的网页抓取（大众点评/小红书页面本体不直接爬取）
- 不做账号系统、权限系统
- 不做地图可视化，仅做列表与距离展示
- 不做复杂推荐算法（先按筛选 + 高分优先）
- 不做后台 CMS 管理页

## Assumptions
- 用户将提供或配置合规聚合 API Key（支持近半年高分数据检索）
- 聚合 API 返回字段可能不完整，允许通过清洗规则补齐或置空
- “最近商区”以餐厅归属商圈字段为准，不做复杂地理反查
- 距离计算使用经纬度球面距离（Haversine）

## Task List

### T001 项目骨架初始化

**Files Involved:**
- Create: `app/main.py`
- Create: `app/config.py`
- Create: `app/database.py`
- Create: `app/models.py`
- Create: `app/schemas.py`
- Create: `app/api/restaurants.py`
- Create: `app/services/query_service.py`
- Create: `app/services/location_service.py`
- Create: `requirements.txt`
- Create: `README.md`

**Steps:**
1. 创建 FastAPI 应用入口与基础路由（`/health`、静态页入口）。
2. 初始化 SQLite 连接、会话管理与 ORM 模型。
3. 定义统一数据结构（餐厅、标签、推荐菜、来源、地理信息）。
4. 添加依赖清单与运行说明。
5. Verify command: `python -m uvicorn app.main:app --reload`
6. Expected result: 服务正常启动，`/health` 返回 200。

**Acceptance Criteria:** 本地可启动 API，数据库可初始化，核心目录结构清晰可复用。

---

### T002 数据模型与筛选字段落库

**Files Involved:**
- Modify: `app/models.py`
- Modify: `app/schemas.py`
- Create: `app/services/filter_options_service.py`

**Steps:**
1. 落地字段：城市、区、热门地点、人均、标签、店名、推荐菜、来源、是否宠物友好、最近商区、评分、经纬度、时间戳。
2. 增加字段规范化策略（标签与推荐菜拆分存储，支持多值）。
3. 提供筛选项聚合接口所需的查询服务。
4. Verify command: `python -m uvicorn app.main:app --reload`
5. Expected result: 字段可完整写入读取；筛选项可聚合。

**Acceptance Criteria:** 数据库和 schema 与页面筛选字段一一对应，无缺失字段。

---

### T003 合规采集器与近半年窗口

**Files Involved:**
- Create: `app/collectors/base.py`
- Create: `app/collectors/aggregator_provider.py`
- Create: `app/services/ingest_service.py`
- Create: `scripts/fetch_restaurants.py`
- Create: `.env.example`

**Steps:**
1. 定义采集器接口（分页抓取、错误重试、限流、窗口参数）。
2. 实现聚合 API 采集逻辑，固定默认窗口 `2025-09-06 ~ 2026-03-06`（支持参数覆盖）。
3. 实现入库清洗：去重（名称+地址近似）、评分标准化、缺失字段容错。
4. 提供命令行采集脚本，支持 `--city shanghai --from --to`。
5. Verify command: `python scripts/fetch_restaurants.py --city shanghai --from 2025-09-06 --to 2026-03-06`
6. Expected result: SQLite 中新增高分餐厅记录，重复数据被合并。

**Acceptance Criteria:** 在有 API Key 的情况下可稳定采集并入库，支持重复执行的增量更新。

---

### T004 查询 API（可复用）

**Files Involved:**
- Modify: `app/api/restaurants.py`
- Modify: `app/services/query_service.py`
- Modify: `app/services/location_service.py`
- Modify: `app/main.py`

**Steps:**
1. 实现 `GET /api/restaurants`（分页、排序、全部筛选字段）。
2. 实现 `GET /api/filter-options`（下拉可选项集合）。
3. 支持传入 `lat/lng`，返回每家餐厅距离（km）。
4. 实现 pet-friendly 布尔筛选与来源筛选。
5. Verify command: `curl "http://127.0.0.1:8000/api/restaurants?city=上海&page=1&page_size=20"`
6. Expected result: 返回结构化 JSON，字段完整，距离计算正确。

**Acceptance Criteria:** API 可被复用；筛选和距离逻辑准确，响应可分页。

---

### T005 前端页面（简单可用）

**Files Involved:**
- Create: `web/index.html`
- Create: `web/styles.css`
- Create: `web/app.js`

**Steps:**
1. 构建固定顶部筛选栏（全部字段使用下拉，店名可文本匹配）。
2. 页面加载默认请求 `city=上海` 并渲染高分列表。
3. 接入浏览器定位授权 API（失败时降级为手动输入位置）。
4. 提供手动位置输入框与“更新位置”动作，触发重新查询并更新距离。
5. 显示核心字段：店名、评分、人均、标签、推荐菜、来源、是否宠物友好、最近商区、距离。
6. Verify command: 打开 `http://127.0.0.1:8000/` 手动验证筛选与定位交互
7. Expected result: 页面可交互，筛选即时生效，距离随位置更新。

**Acceptance Criteria:** 用户无需登录即可完成筛选与查看距离，默认上海数据正确展示。

---

### T006 质量保障与复用文档

**Files Involved:**
- Create: `tests/test_query_api.py`
- Create: `tests/test_distance.py`
- Modify: `README.md`
- Create: `tasks/RUNBOOK.md`

**Steps:**
1. 添加查询 API 与距离计算单测。
2. 文档化配置项（API key、时间窗口、默认城市、分页参数）。
3. 输出运行手册：本地启动、采集、更新、常见故障排查。
4. Verify command: `pytest -q`
5. Expected result: 关键测试通过，README 可独立指导复现。

**Acceptance Criteria:** 项目可复用、可复现，后续仅替换数据源配置即可继续扩展。

## Open Questions
| Question | Background | Decision |
|----------|-----------|----------|
| 聚合 API 供应商具体选择（SerpAPI 或其他） | 不同供应商字段质量和成本差异大 | TBD |
| “高分”阈值是否固定为 `>=4.5` | 会影响结果数量和页面体验 | TBD |
| 热门地点与最近商区字段是否允许为空 | 部分数据源可能不返回完整字段 | TBD |

## Issues Found (Append area)
> 2026-03-06: 当前仓库为空目录，需从 0 初始化项目结构。

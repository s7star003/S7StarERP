# S7StarERP 项目技术文档

---

## 一、项目结构总览

```
S7StarERP/
├── Amazon_api/                # Amazon 相关接口与授权
│   └── Auth/
├── BatchProcessing/           # 批处理脚本
│   └── TikTok/
├── BusinessrRquirements/      # 业务需求文档
├── Config/                    # 各平台配置文件
│   ├── AmazonConfig/
│   ├── SheinConfig/
│   └── ToktokConfig/
├── Datas/                     # 本地数据存储
│   ├── AmazonDatas/
│   ├── SheinDatas/
│   └── TiktokDatas/
├── S7starERPDjango/           # Django 主配置
├── Shein_api/                 # Shein 相关接口与授权
│   ├── Auth/
│   ├── Models/
├── Tiktok_api/                # TikTok 相关接口
│   ├── Auth/                  # 授权与回调
│   ├── DataScience/           # 数据分析接口
│   ├── Models/                # 工具/签名
│   └── Orders/                # 订单相关接口
├── Utils/                     # 工具函数
├── manage.py                  # Django 启动入口
├── requirements.txt           # 依赖列表
└── ...
```

---

## 二、技术栈

- Python 3.x
- Django 5.0.2
- Django REST framework
- drf_yasg（Swagger 文档）
- APScheduler（定时任务）
- requests
- mysqlclient
- python-dotenv
- django-cors-headers

---

## 三、主要模块说明

### 1. TikTok 相关

#### 1.1 授权与回调（Tiktok_api/Auth/）

- `getAuthCode.py`：生成授权 URL，供前端跳转授权。
- `getAccessToken.py`：处理授权回调（/api/TikTok/callback），用 code 换取 token 并保存本地。
- `RefreshToken.py`：刷新 access_token，支持定时任务自动刷新。
- `getAuthCode_script.py`：命令行调试用授权脚本。

#### 1.2 订单接口（Tiktok_api/Orders/）

- `getOrderList.py`：获取订单列表，支持分页与筛选。
- `getOrderDetail.py`：获取订单详情。
- `getPriceDetail.py`：获取订单价格明细。
- `getAllOrder.py`：批量获取所有订单。
- `getOrderAnalysis.py`：订单分析接口。
- `urls.py`：路由注册，所有接口均可在 Swagger 页面测试。

#### 1.3 数据分析（Tiktok_api/DataScience/）

- `BuyerAnalysis.py`：买家分析。
- `getAreaDemand_7d/30d/all.py`：区域需求分析。
- `getProfitAnalysis.py`：利润分析。
- `getRepurchaseRate.py`：复购率分析。
- `getReturnRate.py`：退货率分析。
- `getSalesRank_7d/30d/all.py`：商品销售排行。
- `getMonthlySalesAnalysis.py`：月度销售分析。
- `urls.py`：数据分析相关接口路由。

#### 1.4 数据模型与工具（Tiktok_api/Models/）

- `sign_utils.py`：签名工具函数。

---

### 2. Shein 相关

- `Auth/`：授权、回调、签名生成等。
- `Models/`：签名算法等。

---

### 3. Amazon 相关

- `Auth/`：授权、回调、token 刷新等。

---

### 4. 批处理脚本（BatchProcessing/TikTok/）

- `SyncTiktokOrderLists.py`：批量同步 TikTok 订单。
- `BuyerAnalysis.py`：批量买家分析。
- `TikTokOrderAnalysis.py`：订单分析批处理。
- `MultiplatformData.py`：多平台数据处理。
- `batchGetOrderPriceDetail.py`：批量获取订单价格明细。

---

### 5. 配置与数据

- `Config/`：各平台 API 配置（如 client_id、secret、回调地址等）。
- `Datas/`：本地数据缓存（如 token、订单、价格明细等 JSON 文件）。

---

### 6. 业务需求与文档

- `BusinessrRquirements/`：需求文档、数据看板说明、token 刷新说明等。

---

## 四、接口路由示例

### TikTok 订单相关（Tiktok_api/Orders/urls.py）

- `/api/TikTok/order/list/`         获取订单列表
- `/api/TikTok/order/detail/`       获取订单详情
- `/api/TikTok/order/price_detail/` 获取订单价格明细
- `/api/TikTok/order/all/`          获取所有订单
- `/api/TikTok/order/analysis/`     订单分析
- `/api/TikTok/callback`            授权回调
- `/api/TikTok/auth_url/`           获取授权 URL
- `/api/TikTok/refresh_token`       刷新 token
- `/api/TikTok/swagger/`            Swagger 文档页面

### TikTok 数据分析（Tiktok_api/DataScience/urls.py）

- `/api/TikTok/DataScience/BuyerAnalysis/`         买家分析
- `/api/TikTok/DataScience/AreaDemand_7d/`         7天区域需求
- `/api/TikTok/DataScience/ProfitAnalysis/`        利润分析
- `/api/TikTok/DataScience/RepurchaseRate/`        复购率
- `/api/TikTok/DataScience/ReturnRate/`            退货率
- `/api/TikTok/DataScience/SalesRank_7d/`          7天销售排行
- `/api/TikTok/DataScience/getMonthlySalesAnalysis/` 月度销售分析
- ...（详见 urls.py）

---

## 五、定时任务与自动化

- APScheduler 集成于 Django App `apps.py`，实现每天 0 点自动刷新 TikTok token。
- 服务启动时自动刷新一次 token，确保 token 有效。

---

## 六、Swagger 文档

- 所有接口均已注册 Swagger，可在 `/api/TikTok/swagger/` 页面可视化测试。
- 权限设置为 `AllowAny`，无需登录即可调试。

---

## 七、数据存储

- `Datas/TiktokDatas/`：存储 token、订单、价格明细等 JSON 文件，供接口与分析脚本读取。
- `Config/`：各平台 API 配置，敏感信息建议用 .env 管理。

---

## 八、开发与运维建议

- 端口建议使用 8000，避免 8080 被占用导致假死或 401。
- 批处理脚本保持轻量、函数式，服务端接口分层清晰。
- 依赖管理见 `requirements.txt`，如需扩展请同步更新。
- 业务需求与数据看板文档见 `BusinessrRquirements/`。

---

如需详细接口参数、示例、异常处理等，可进一步补充接口级文档。 
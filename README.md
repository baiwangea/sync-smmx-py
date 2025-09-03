[English](#english) | [中文](#中文)

---

# SMM-X Sync Service <a name="english"></a>

This project is a high-performance, robust service designed to synchronize data between a third-party supplier API and the SMM-X platform. It handles orders, prices, and statuses, while also performing daily balance checks.

The service is built with a focus on modularity, maintainability, and performance, featuring concurrent task execution, a resilient API client, and an optimized database structure.

## Core Features

- **Order Synchronization**: Every minute, fetches new orders from the supplier and places them on the SMM-X platform.
- **Price Synchronization**: Periodically syncs product prices from the supplier to SMM-X.
- **Status Synchronization**: Periodically checks for status updates of active orders on SMM-X and updates the local database.
- **Daily Balance Check**: Every day at midnight, fetches the SMM-X account balance and logs it to a file.
- **Product Mapping**: A flexible system to map supplier product IDs to your internal SMM-X service IDs.
- **High Performance**: All scheduled tasks run in separate threads to prevent blocking, ensuring that frequent jobs (like order syncing) are not delayed by less frequent or long-running ones.
- **Robustness**: The API client includes automatic retries with exponential backoff for common network/server errors. Detailed error logging is implemented for all services.

## Project Structure

```
syncSmmX/
├── main.py             # Main application entry point: initializes and schedules all tasks.
├── config.py           # Manages all configuration via environment variables.
├── database.py         # Handles database initialization, connection, and schema.
├── api_client.py       # A generic, robust API client for communicating with external services.
├── order_syncer.py     # Contains the logic for synchronizing new orders.
├── price_syncer.py     # Contains the logic for synchronizing prices.
├── status_syncer.py    # Contains the logic for synchronizing order statuses.
├── balance_checker.py  # Contains the logic for checking and logging account balance.
├── product_mapper.py   # Manages the mapping between supplier and local product IDs.
└── README.md           # This file.
```

## Setup and Configuration

### 1. Dependencies

Install the required Python libraries. It is recommended to use a virtual environment.

```bash
pip install schedule requests
```

### 2. Environment Variables

The application is configured using environment variables. Create a `.env` file in the project root or set these variables in your shell before running the application.

```
# Supplier API Configuration
SUPPLIER_API_URL="https://console-docs.apipost.cn/preview/bd5562d43f91d43b/2c389668408f0236?target_id=9002ae07-1333-4182-b39b-2e77c9ee8ddd"
SUPPLIER_API_KEY="your_supplier_api_key_here"

# SMM-X API Configuration
SMMX_API_URL="https://smm-x.com/api"
SMMX_API_KEY="f311620fc24d9b3ab97d82bc898bc32a"

# File Paths (optional, defaults are provided)
DB_FILE="database.sqlite"
BALANCE_LOG_FILE="balance_log.txt"
```

## How to Run

To start the service, simply run the `main.py` script:

```bash
python main.py
```

The service will start, initialize all components, and begin executing the scheduled tasks. All activities and errors will be printed to the console.

## API Documentation

- **Supplier Platform API**: [Supplier API Docs](https://console-docs.apipost.cn/preview/bd5562d43f91d43b/2c389668408f0236?target_id=9002ae07-1333-4182-b39b-2e77c9ee8ddd)
- **SMM-X Platform API**: [SMM-X API Docs](https://smm-x.com/api)

---

# SMM-X 同步服务 <a name="中文"></a>

本项目是一个高性能、高健壮性的服务，用于在第三方供应商 API 和 SMM-X 平台之间同步数据。它能处理订单、价格和状态的同步，并执行每日余额检查。

该服务在构建时充分考虑了模块化、可维护性和性能，实现了并发任务执行、弹性的 API 客户端和优化的数据库结构。

##核心功能

- **订单同步**: 每分钟从供应商处获取新订单，并将其同步到 SMM-X 平台。
- **价格同步**: 定期将供应商的商品价格同步到 SMM-X。
- **状态同步**: 定期从 SMM-X 查询活动订单的状态，并更新本地数据库。
- **每日余额检查**: 每天午夜，获取 SMM-X 账户余额并记录到日志文件中。
- **商品映射**: 提供灵活的系统，用于将供应商商品 ID 映射到您的内部 SMM-X 服务 ID。
- **高性能**: 所有计划任务都在独立的线程中运行，以防阻塞。这确保了高频任务（如订单同步）不会被低频或耗时较长的任务延迟。
- **高健壮性**: API 客户端包含针对常见网络/服务器错误的自动重试机制（带指数退避）。所有服务都实现了详细的错误日志记录。

## 项目结构

```
syncSmmX/
├── main.py             # 主程序入口：初始化并调度所有任务。
├── config.py           # 通过环境变量管理所有配置。
├── database.py         # 处理数据库初始化、连接和结构。
├── api_client.py       # 用于与外部服务通信的通用、健壮的API客户端。
├── order_syncer.py     # 包含同步新订单的逻辑。
├── price_syncer.py     # 包含同步价格的逻辑。
├── status_syncer.py    # 包含同步订单状态的逻辑。
├── balance_checker.py  # 包含检查和记录账户余额的逻辑。
├── product_mapper.py   # 管理供应商和本地商品ID之间的映射。
└── README.md           # 本文件。
```

## 设置与配置

### 1. 依赖安装

安装所需的 Python 库。建议在虚拟环境中使用。

```bash
pip install schedule requests
```

### 2. 环境变量

本应用通过环境变量进行配置。您可以在项目根目录创建一个 `.env` 文件，或在运行应用前在 shell 中设置这些变量。

```
# 供应商 API 配置
SUPPLIER_API_URL="https://console-docs.apipost.cn/preview/bd5562d43f91d43b/2c389668408f0236?target_id=9002ae07-1333-4182-b39b-2e77c9ee8ddd"
SUPPLIER_API_KEY="your_supplier_api_key_here"

# SMM-X API 配置
SMMX_API_URL="https://smm-x.com/api"
SMMX_API_KEY="f311620fc24d9b3ab97d82bc898bc32a"

# 文件路径 (可选, 已提供默认值)
DB_FILE="database.sqlite"
BALANCE_LOG_FILE="balance_log.txt"
```

## 如何运行

要启动此服务，只需运行 `main.py` 脚本：

```bash
python main.py
```

服务将会启动，初始化所有组件，并开始执行计划任务。所有的活动和错误信息都将打印到控制台。

## API 文档

- **源平台接口文档**: [源平台 API 文档](https://console-docs.apipost.cn/preview/bd5562d43f91d43b/2c389668408f0236?target_id=9002ae07-1333-4182-b39b-2e77c9ee8ddd)
- **目标平台接口文档**: [目标平台 API 文档](https://smm-x.com/api)

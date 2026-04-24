# 需求與系統設計規格

## 1. 需求細節 (基於現有 `math_lib.py` 擴充之假設)
因為未提供具體業務需求，根據工作區現有的 `math_lib.py` (包含基本的數學運算) 以及 `README.md` 中的 "TODO: Add more functions to math_lib"，我們將需求定義為：
**建構一個「線上數學運算 API 服務」，提供基本的數學運算功能，並將使用者的計算歷史記錄儲存至資料庫中。**

具體功能包含：
- 執行基本數學運算 (加、減、乘、除等)。
- 查詢歷史運算記錄。

## 2. API 規格設計 (RESTful API)

### 2.1 執行數學運算
- **Endpoint**: `POST /api/v1/calculate`
- **Description**: 執行指定的數學運算並記錄至資料庫。
- **Request Body**:
  ```json
  {
    "operation": "add",   // 支援: add, subtract, multiply, divide
    "operand_a": 10.5,
    "operand_b": 5.0
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "id": 1,
      "result": 15.5
    }
  }
  ```
- **Response (400 Bad Request)**:
  ```json
  {
    "status": "error",
    "message": "Invalid operation or division by zero"
  }
  ```

### 2.2 取得運算歷史記錄
- **Endpoint**: `GET /api/v1/history`
- **Description**: 取得過去所有的數學運算記錄。
- **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": [
      {
        "id": 1,
        "operation": "add",
        "operand_a": 10.5,
        "operand_b": 5.0,
        "result": 15.5,
        "created_at": "2023-10-01T12:00:00Z"
      }
    ]
  }
  ```

## 3. 資料庫綱要設計 (Database Schema)

我們將設計一個關聯式資料庫表格來儲存運算記錄。

### Table: `calculation_history`
| 欄位名稱 (Column) | 資料型別 (Type) | 約束條件 (Constraints) | 描述 (Description) |
| --- | --- | --- | --- |
| `id` | Integer | Primary Key, Auto Increment | 記錄的唯一識別碼 |
| `operation` | VARCHAR(50) | Not Null | 運算類型 (如 add, subtract) |
| `operand_a` | FLOAT | Not Null | 第一個運算元 |
| `operand_b` | FLOAT | Not Null | 第二個運算元 |
| `result` | FLOAT | Not Null | 運算結果 |
| `created_at` | TIMESTAMP | Default CURRENT_TIMESTAMP | 執行運算的時間 |

erDiagram
    Users {
        INTEGER id PK
        TEXT username UNIQUE
        TEXT password
        TEXT email UNIQUE
        DATETIME created_at
    }
    Departments {
        INTEGER id PK
        TEXT name UNIQUE
        INTEGER manager_id FK
        DATETIME created_at
    }
    Products {
        INTEGER id PK
        TEXT name
        TEXT description
        REAL price
        INTEGER stock_quantity
        DATETIME created_at
    }
    Orders {
        INTEGER id PK
        INTEGER user_id FK
        DATETIME order_date
        TEXT status
        REAL total
    }
    Suppliers {
        INTEGER id PK
        TEXT name UNIQUE
        TEXT contact_email UNIQUE
        TEXT phone_number
        TEXT address
        DATETIME created_at
    }
    Order_Items {
        INTEGER id PK
        INTEGER order_id FK
        INTEGER product_id FK
        INTEGER quantity
        REAL price
    }
    Sales_Invoices {
        INTEGER id PK
        INTEGER order_id FK
        DATETIME invoice_date
        REAL total_amount
    }
    Purchase_Invoices {
        INTEGER id PK
        INTEGER supplier_id FK
        DATETIME invoice_date
        REAL total_amount
    }
    Purchase_Orders {
        INTEGER id PK
        INTEGER supplier_id FK
        INTEGER user_id FK
        DATETIME order_date
        TEXT status
        REAL total
    }
    Purchase_Order_Items {
        INTEGER id PK
        INTEGER purchase_order_id FK
        INTEGER product_id FK
        INTEGER quantity
        REAL price
    }

    Users ||--o{ Departments: manages
    Users ||--o{ Orders: places
    Orders ||--o{ Order_Items: contains
    Products ||--o{ Order_Items: included_in
    Orders ||--o{ Sales_Invoices: generates
    Suppliers ||--o{ Purchase_Invoices: receives
    Users ||--o{ Purchase_Orders: creates
    Suppliers ||--o{ Purchase_Orders: supplies
    Purchase_Orders ||--o{ Purchase_Order_Items: contains
    Products ||--o{ Purchase_Order_Items: included_in
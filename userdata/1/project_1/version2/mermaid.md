erDiagram
    Users {
        INTEGER id PK "AUTOINCREMENT"
        TEXT username "NOT NULL, UNIQUE"
        TEXT password "NOT NULL"
        TEXT email "NOT NULL, UNIQUE"
        DATETIME created_at "DEFAULT CURRENT_TIMESTAMP"
    }
    
    Departments {
        INTEGER id PK "AUTOINCREMENT"
        TEXT name "NOT NULL, UNIQUE"
        INTEGER manager_id
        DATETIME created_at "DEFAULT CURRENT_TIMESTAMP"
    }

    Products {
        INTEGER id PK "AUTOINCREMENT"
        TEXT name "NOT NULL"
        TEXT description
        REAL price "NOT NULL"
        INTEGER stock_quantity "NOT NULL CHECK (stock_quantity >= 0)"
        DATETIME created_at "DEFAULT CURRENT_TIMESTAMP"
    }

    Orders {
        INTEGER id PK "AUTOINCREMENT"
        INTEGER user_id "NOT NULL"
        DATETIME order_date "DEFAULT CURRENT_TIMESTAMP"
        TEXT status "NOT NULL"
        REAL total "NOT NULL"
    }

    Suppliers {
        INTEGER id PK "AUTOINCREMENT"
        TEXT name "NOT NULL, UNIQUE"
        TEXT contact_email "NOT NULL, UNIQUE"
        TEXT phone_number
        TEXT address
        DATETIME created_at "DEFAULT CURRENT_TIMESTAMP"
    }

    Order_Items {
        INTEGER id PK "AUTOINCREMENT"
        INTEGER order_id "NOT NULL"
        INTEGER product_id "NOT NULL"
        INTEGER quantity "NOT NULL"
        REAL price "NOT NULL"
    }

    Sales_Invoices {
        INTEGER id PK "AUTOINCREMENT"
        INTEGER order_id "NOT NULL"
        DATETIME invoice_date "DEFAULT CURRENT_TIMESTAMP"
        REAL total_amount "NOT NULL"
    }

    Purchase_Invoices {
        INTEGER id PK "AUTOINCREMENT"
        INTEGER supplier_id "NOT NULL"
        DATETIME invoice_date "DEFAULT CURRENT_TIMESTAMP"
        REAL total_amount "NOT NULL"
    }

    Users ||--o{ Departments : manages
    Users ||--o{ Orders : places
    Orders ||--o{ Order_Items : contains
    Products ||--o{ Order_Items : includes
    Orders ||--o{ Sales_Invoices : generates
    Suppliers ||--o{ Purchase_Invoices : provides
erDiagram
    Users {
        INTEGER PRIMARY KEY AUTOINCREMENT id
        TEXT username UNIQUE
        TEXT password
        TEXT email UNIQUE
        DATETIME created_at
    }
    Departments {
        INTEGER PRIMARY KEY AUTOINCREMENT id
        TEXT name UNIQUE
        INTEGER manager_id
        DATETIME created_at
    }
    Products {
        INTEGER PRIMARY KEY AUTOINCREMENT id
        TEXT name
        TEXT description
        REAL price
        INTEGER stock_quantity
        DATETIME created_at
    }
    Orders {
        INTEGER PRIMARY KEY AUTOINCREMENT id
        INTEGER user_id
        DATETIME order_date
        TEXT status
        REAL total
    }
    Suppliers {
        INTEGER PRIMARY KEY AUTOINCREMENT id
        TEXT name UNIQUE
        TEXT contact_email UNIQUE
        TEXT phone_number
        TEXT address
        DATETIME created_at
    }
    Order_Items {
        INTEGER PRIMARY KEY AUTOINCREMENT id
        INTEGER order_id
        INTEGER product_id
        INTEGER quantity
        REAL price
    }
    Sales_Invoices {
        INTEGER PRIMARY KEY AUTOINCREMENT id
        INTEGER order_id
        DATETIME invoice_date
        REAL total_amount
    }
    Purchase_Invoices {
        INTEGER PRIMARY KEY AUTOINCREMENT id
        INTEGER supplier_id
        DATETIME invoice_date
        REAL total_amount
    }
    Purchase_Orders {
        INTEGER PRIMARY KEY AUTOINCREMENT id
        INTEGER supplier_id
        INTEGER user_id
        DATETIME order_date
        TEXT status
        REAL total
    }
    Purchase_Order_Items {
        INTEGER PRIMARY KEY AUTOINCREMENT id
        INTEGER purchase_order_id
        INTEGER product_id
        INTEGER quantity
        REAL price
    }

    Users ||--o{ Departments : manages
    Users ||--o{ Orders : places
    Users ||--o{ Purchase_Orders : creates
    Products ||--o{ Order_Items : contains
    Orders ||--o{ Order_Items : includes
    Orders ||--|{ Sales_Invoices : generates
    Suppliers ||--o{ Purchase_Invoices : issues
    Suppliers ||--o{ Purchase_Orders : supplies
    Products ||--o{ Purchase_Order_Items : includes
    Purchase_Orders ||--o{ Purchase_Order_Items : consists_of
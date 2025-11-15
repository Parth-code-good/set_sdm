erDiagram
    Users {
        INTEGER id PK
        TEXT username
        TEXT password
        TEXT email
        DATETIME created_at
    }
    Departments {
        INTEGER id PK
        TEXT name
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
        TEXT name
        TEXT contact_email
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

    Users ||--o{ Departments : manages
    Users ||--o{ Orders : places
    Orders ||--o{ Order_Items : contains
    Products ||--o{ Order_Items : included_in
    Departments ||--o{ Users : employs
    Suppliers ||--o{ Products : supplies
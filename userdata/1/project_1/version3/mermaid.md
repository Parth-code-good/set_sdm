erDiagram

    Users {
        int id PK
        string username
        string password
        string email
        datetime created_at
    }

    Departments {
        int id PK
        string name
        int manager_id FK
        datetime created_at
    }

    Products {
        int id PK
        string name
        string description
        float price
        int stock_quantity
        datetime created_at
    }

    Orders {
        int id PK
        int user_id FK
        datetime order_date
        string status
        float total
    }

    Suppliers {
        int id PK
        string name
        string contact_email
        string phone_number
        string address
        datetime created_at
    }

    OrderItems {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        float price
    }

    SalesInvoices {
        int id PK
        int order_id FK
        datetime invoice_date
        float total_amount
    }

    PurchaseInvoices {
        int id PK
        int supplier_id FK
        datetime invoice_date
        float total_amount
    }

    %% RELATIONSHIPS
    Users ||--o{ Departments : "manages"
    Users ||--o{ Orders : "places"
    Orders ||--o{ OrderItems : "contains"
    Products ||--o{ OrderItems : "has"
    Orders ||--o{ SalesInvoices : "generates"
    Suppliers ||--o{ PurchaseInvoices : "issues"

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
        int manager_id
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
        int user_id
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
    Order_Items {
        int id PK
        int order_id
        int product_id
        int quantity
        float price
    }
    Sales_Invoices {
        int id PK
        int order_id
        datetime invoice_date
        float total_amount
    }
    Purchase_Invoices {
        int id PK
        int supplier_id
        datetime invoice_date
        float total_amount
    }
    Purchase_Orders {
        int id PK
        int supplier_id
        int user_id
        datetime order_date
        string status
        float total
    }
    Purchase_Order_Items {
        int id PK
        int purchase_order_id
        int product_id
        int quantity
        float price
    }
    Departments }o--|| Users : manager_id to id
    Orders }o--|| Users : user_id to id
    Order_Items }o--|| Orders : order_id to id
    Order_Items }o--|| Products : product_id to id
    Sales_Invoices }o--|| Orders : order_id to id
    Purchase_Invoices }o--|| Suppliers : supplier_id to id
    Purchase_Orders }o--|| Suppliers : supplier_id to id
    Purchase_Orders }o--|| Users : user_id to id
    Purchase_Order_Items }o--|| Purchase_Orders : purchase_order_id to id
    Purchase_Order_Items }o--|| Products : product_id to id
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

    OrderItems {
        int id PK
        int order_id
        int product_id
        int quantity
        float price
    }

    SalesInvoices {
        int id PK
        int order_id
        datetime invoice_date
        float total_amount
    }

    PurchaseInvoices {
        int id PK
        int supplier_id
        datetime invoice_date
        float total_amount
    }

    PurchaseOrders {
        int id PK
        int supplier_id
        int user_id
        datetime order_date
        string status
        float total
    }

    PurchaseOrderItems {
        int id PK
        int purchase_order_id
        int product_id
        int quantity
        float price
    }

    Departments }o--|| Users : manager_id to id
    Orders }o--|| Users : user_id to id
    OrderItems }o--|| Orders : order_id to id
    OrderItems }o--|| Products : product_id to id
    SalesInvoices }o--|| Orders : order_id to id
    PurchaseInvoices }o--|| Suppliers : supplier_id to id
    PurchaseOrders }o--|| Suppliers : supplier_id to id
    PurchaseOrders }o--|| Users : user_id to id
    PurchaseOrderItems }o--|| PurchaseOrders : purchase_order_id to id
    PurchaseOrderItems }o--|| Products : product_id to id

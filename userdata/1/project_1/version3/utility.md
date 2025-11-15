# Utility Table

This file explains why each table exists and the purpose of key attributes.

## Table `Users`
| Column | Suggested Purpose |
|---|---|
| `id` | (explain why `id` exists; e.g., identifier, timestamp, FK to other table) |
| `username` | (explain why `username` exists; e.g., identifier, timestamp, FK to other table) |
| `password` | (explain why `password` exists; e.g., identifier, timestamp, FK to other table) |
| `email` | (explain why `email` exists; e.g., identifier, timestamp, FK to other table) |
| `created_at` | (explain why `created_at` exists; e.g., identifier, timestamp, FK to other table) |

## Table `Departments`
| Column | Suggested Purpose |
|---|---|
| `id` | (explain why `id` exists; e.g., identifier, timestamp, FK to other table) |
| `name` | (explain why `name` exists; e.g., identifier, timestamp, FK to other table) |
| `manager_id` | (explain why `manager_id` exists; e.g., identifier, timestamp, FK to other table) |
| `created_at` | (explain why `created_at` exists; e.g., identifier, timestamp, FK to other table) |
| `FOREIGN` | (explain why `FOREIGN` exists; e.g., identifier, timestamp, FK to other table) |

## Table `Products`
| Column | Suggested Purpose |
|---|---|
| `id` | (explain why `id` exists; e.g., identifier, timestamp, FK to other table) |
| `name` | (explain why `name` exists; e.g., identifier, timestamp, FK to other table) |
| `description` | (explain why `description` exists; e.g., identifier, timestamp, FK to other table) |
| `price` | (explain why `price` exists; e.g., identifier, timestamp, FK to other table) |
| `stock_quantity` | (explain why `stock_quantity` exists; e.g., identifier, timestamp, FK to other table) |
| `created_at` | (explain why `created_at` exists; e.g., identifier, timestamp, FK to other table) |

## Table `Orders`
| Column | Suggested Purpose |
|---|---|
| `id` | (explain why `id` exists; e.g., identifier, timestamp, FK to other table) |
| `user_id` | (explain why `user_id` exists; e.g., identifier, timestamp, FK to other table) |
| `order_date` | (explain why `order_date` exists; e.g., identifier, timestamp, FK to other table) |
| `status` | (explain why `status` exists; e.g., identifier, timestamp, FK to other table) |
| `total` | (explain why `total` exists; e.g., identifier, timestamp, FK to other table) |
| `FOREIGN` | (explain why `FOREIGN` exists; e.g., identifier, timestamp, FK to other table) |

## Table `Suppliers`
| Column | Suggested Purpose |
|---|---|
| `id` | (explain why `id` exists; e.g., identifier, timestamp, FK to other table) |
| `name` | (explain why `name` exists; e.g., identifier, timestamp, FK to other table) |
| `contact_email` | (explain why `contact_email` exists; e.g., identifier, timestamp, FK to other table) |
| `phone_number` | (explain why `phone_number` exists; e.g., identifier, timestamp, FK to other table) |
| `address` | (explain why `address` exists; e.g., identifier, timestamp, FK to other table) |
| `created_at` | (explain why `created_at` exists; e.g., identifier, timestamp, FK to other table) |

## Table `Order_Items`
| Column | Suggested Purpose |
|---|---|
| `id` | (explain why `id` exists; e.g., identifier, timestamp, FK to other table) |
| `order_id` | (explain why `order_id` exists; e.g., identifier, timestamp, FK to other table) |
| `product_id` | (explain why `product_id` exists; e.g., identifier, timestamp, FK to other table) |
| `quantity` | (explain why `quantity` exists; e.g., identifier, timestamp, FK to other table) |
| `price` | (explain why `price` exists; e.g., identifier, timestamp, FK to other table) |
| `FOREIGN` | (explain why `FOREIGN` exists; e.g., identifier, timestamp, FK to other table) |
| `FOREIGN` | (explain why `FOREIGN` exists; e.g., identifier, timestamp, FK to other table) |

## Table `Sales_Invoices`
| Column | Suggested Purpose |
|---|---|
| `id` | (explain why `id` exists; e.g., identifier, timestamp, FK to other table) |
| `order_id` | (explain why `order_id` exists; e.g., identifier, timestamp, FK to other table) |
| `invoice_date` | (explain why `invoice_date` exists; e.g., identifier, timestamp, FK to other table) |
| `total_amount` | (explain why `total_amount` exists; e.g., identifier, timestamp, FK to other table) |
| `FOREIGN` | (explain why `FOREIGN` exists; e.g., identifier, timestamp, FK to other table) |

## Table `Purchase_Invoices`
| Column | Suggested Purpose |
|---|---|
| `id` | (explain why `id` exists; e.g., identifier, timestamp, FK to other table) |
| `supplier_id` | (explain why `supplier_id` exists; e.g., identifier, timestamp, FK to other table) |
| `invoice_date` | (explain why `invoice_date` exists; e.g., identifier, timestamp, FK to other table) |
| `total_amount` | (explain why `total_amount` exists; e.g., identifier, timestamp, FK to other table) |
| `FOREIGN` | (explain why `FOREIGN` exists; e.g., identifier, timestamp, FK to other table) |


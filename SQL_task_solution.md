## Таблицы и их поля

### 1. Invoices (Счета)
- `InvoiceID` (INT, PK): Уникальный идентификатор счета.
- `InvoiceNumber` (VARCHAR): Номер счета. Важно учитывать, что нумерация может начинаться заново с определенной даты.
- `InvoiceDate` (DATE): Дата выставления счета.
- `Amount` (DECIMAL): Сумма счета.
- `ManagerID` (INT, FK): Идентификатор менеджера, который выставил счет. Связь с таблицей Managers.
- `CustomerID` (INT, FK): Идентификатор контрагента (клиента). Связь с таблицей Customers.
- `Status` (VARCHAR): Статус счета (например, "выставлен", "оплачен", "отменен").
- `Details` (TEXT): Подробности по счету (список товаров/услуг и их описание).
- `PaymentStatus` (VARCHAR): Статус оплаты счета. Возможные значения: "не оплачен", "частично оплачен", "полностью оплачен".
- `PaymentAmount` (DECIMAL): Сумма оплаченной части счета.
- `ShippingStatus` (VARCHAR): Статус отгрузки счета. 
Возможные значения: "не отгружен", "частично отгружен", "полностью отгружен".
- `LastSyncDate` (DATETIME): Дата последней синхронизации с внешней бухгалтерской системой. 
Отслеживание актуальности данных.
### 2. Managers (Менеджеры)
- `ManagerID` (INT, PK): Уникальный идентификатор менеджера.
- `ManagerName` (VARCHAR): Имя менеджера.
- `Department` (VARCHAR): Отдел, к которому принадлежит менеджер.
### 3. Customers (Контрагенты)
- `CustomerID` (INT, PK): Уникальный идентификатор контрагента.
- `CustomerName` (VARCHAR): Имя контрагента.
- `TIN` (VARCHAR): ИНН контрагента.
### 4. InvoiceHistory (История изменений)
- `HistoryID` (INT, PK): Уникальный идентификатор записи.
- `InvoiceID` (INT, FK): Идентификатор счета. Связь с таблицей Invoices.
- `ChangeDate` (DATETIME): Дата изменения.
- `Status` (VARCHAR): Новый статус счета.
- `ChangedBy` (INT, FK): Идентификатор менеджера, который произвел изменение. Связь с таблицей Managers.
- `PaymentStatus` (VARCHAR): Статус оплаты на момент изменения.
- `PaymentAmount` (DECIMAL): Оплаченная сумма на момент изменения.
- `ShippingStatus` (VARCHAR): Статус отгрузки на момент изменения.

## Связи между таблицами
Связи между таблицами
- Invoices.ManagerID --> Managers.ManagerID
- Invoices.CustomerID --> Customers.CustomerID
- InvoiceHistory.InvoiceID --> Invoices.InvoiceID

## Индексы и их назначение
### 1. Индекс для поиска последних счетов
```sql
CREATE INDEX idx_invoices_manager_date ON Invoices (ManagerID, InvoiceDate DESC);
```
### 2. Индекс для поиска счетов по контрагенту
```sql
CREATE INDEX idx_invoices_customer ON Invoices (CustomerID);
```
### 3. Индекс для поиска счетов по номеру
```sql
CREATE INDEX idx_invoices_number ON Invoices (InvoiceNumber, InvoiceDate);
```
### 4. Индекс для поиска истории изменений счетов
```sql
CREATE INDEX idx_invoice_history ON InvoiceHistory (InvoiceID, ChangeDate);
```
### 5. Индекс по статусу оплаты и отгрузки (для решения бонус уровня)
```sql
CREATE INDEX idx_invoices_payment_shipping_status ON Invoices (PaymentStatus, ShippingStatus);
```
### 6. Индекс по дате последней синхронизации (для решения бонус уровня)
```sql
CREATE INDEX idx_invoices_last_sync_date ON Invoices (LastSyncDate);
```
### 7. Индекс по сумме оплаты (для решения бонус уровня)
```sql
CREATE INDEX idx_invoices_payment_amount ON Invoices (PaymentAmount);
```


## Запросы для типовых выборок
### 1. Последние 20 счетов менеджера
```sql
SELECT *
FROM Invoices
WHERE ManagerID = @ManagerID
ORDER BY InvoiceDate DESC
LIMIT 20;
```
### 2. Поиск счетов по контрагенту
```sql
SELECT *
FROM Invoices
WHERE CustomerID = @CustomerID;
```
### 3. Поиск счета по номеру
```sql
SELECT *
FROM Invoices
WHERE InvoiceNumber = @InvoiceNumber
ORDER BY InvoiceDate DESC;
```
### 4. История изменений счета
```sql
SELECT *
FROM InvoiceHistory
WHERE InvoiceID = @InvoiceID
ORDER BY ChangeDate;
```
### 5. Поиск счетов за прошлую неделю/месяц/год
```sql
SELECT *
FROM Invoices
WHERE InvoiceDate BETWEEN @StartDate AND @EndDate;
```
### 6. Счета, которые оплачены, но не отгружены (для решения бонус уровня)
```sql
SELECT *
FROM Invoices
WHERE PaymentStatus = 'полностью оплачен'
  AND ShippingStatus = 'не отгружен';
```
### 7. Счета, которые отгружены, но не оплачены (для решения бонус уровня)
```sql
SELECT *
FROM Invoices
WHERE ShippingStatus = 'полностью отгружен'
  AND (PaymentStatus = 'не оплачен' OR PaymentStatus = 'частично оплачен');
```
### 8. Выборка для синхронизации (счета, которые изменялись с момента последней синхронизации) (для решения бонус уровня)
```sql
SELECT *
FROM Invoices
WHERE LastSyncDate < NOW() - INTERVAL 1 DAY;
```
### 9. Выборка счетов для обновления статусов (для решения бонус уровня)
```sql
SELECT i.InvoiceID, i.InvoiceNumber, i.PaymentStatus, i.ShippingStatus, b.PaymentStatus AS NewPaymentStatus, b.ShippingStatus AS NewShippingStatus
FROM Invoices i
LEFT JOIN ExternalBillingSystem b ON i.InvoiceNumber = b.InvoiceNumber
WHERE i.PaymentStatus != b.PaymentStatus OR i.ShippingStatus != b.ShippingStatus;
```

## Дополнительные стратегии синхронизации
- Использовать задание (job) или хранимую процедуру для регулярного обновления данных 
о статусах оплаты и отгрузки из внешней системы.
Выбирать только те счета, которые изменялись с последней синхронизации, используя поле LastSyncDate.
- Ввести дополнительную таблицу для логирования ошибок синхронизации, чтобы отслеживать и исправлять проблемы.
- Создать триггеры на обновление полей PaymentStatus и ShippingStatus в таблице Invoices, 
чтобы автоматически обновлять поле LastSyncDate.

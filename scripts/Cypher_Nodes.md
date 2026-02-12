## Load Nodes

**Load Categories:**
```cypher
LOAD CSV WITH HEADERS FROM "file:///categories.csv" AS row
MERGE (c:Category {categoryID: toInteger(row.categoryID)})
SET c.categoryName = row.categoryName,
    c.description = row.description;
```

**Load Customers:**
```cypher
LOAD CSV WITH HEADERS FROM "file:///customers.csv" AS row
MERGE (c:Customer {customerID: row.customerID})
SET c.companyName = row.companyName,
    c.contactName = row.contactName,
    c.contactTitle = row.contactTitle,
    c.address = row.address,
    c.city = row.city,
    c.region = row.region,
    c.postalCode = row.postalCode,
    c.country = row.country,
    c.phone = row.phone,
    c.fax = row.fax;
```

**Load Employees:**
```cypher
LOAD CSV WITH HEADERS FROM "file:///employees.csv" AS row
MERGE (e:Employee {employeeID: toInteger(row.employeeID)})
SET e.lastName = row.lastName,
    e.firstName = row.firstName,
    e.title = row.title,
    e.titleOfCourtesy = row.titleOfCourtesy,
    e.birthDate = row.birthDate,
    e.hireDate = row.hireDate,
    e.address = row.address,
    e.city = row.city,
    e.region = row.region,
    e.postalCode = row.postalCode,
    e.country = row.country,
    e.homePhone = row.homePhone,
    e.extension = row.extension,
    e.notes = row.notes,
    e.photoPath = row.photoPath;
```

**Load Suppliers:**
```cypher
LOAD CSV WITH HEADERS FROM "file:///suppliers.csv" AS row
MERGE (s:Supplier {supplierID: toInteger(row.supplierID)})
SET s.companyName = row.companyName,
    s.contactName = row.contactName,
    s.contactTitle = row.contactTitle,
    s.address = row.address,
    s.city = row.city,
    s.region = row.region,
    s.postalCode = row.postalCode,
    s.country = row.country,
    s.phone = row.phone,
    s.fax = row.fax,
    s.homePage = row.homePage;
```

**Load Products:**
```cypher
LOAD CSV WITH HEADERS FROM "file:///products.csv" AS row
MERGE (p:Product {productID: toInteger(row.productID)})
SET p.productName = row.productName,
    p.quantityPerUnit = row.quantityPerUnit,
    p.unitPrice = toFloat(row.unitPrice),
    p.unitsInStock = toInteger(row.unitsInStock),
    p.unitsOnOrder = toInteger(row.unitsOnOrder),
    p.reorderLevel = toInteger(row.reorderLevel),
    p.discontinued = (row.discontinued <> "0");
```

**Load Shippers:**
```cypher
LOAD CSV WITH HEADERS FROM "file:///shippers.csv" AS row
MERGE (s:Shipper {shipperID: toInteger(row.shipperID)})
SET s.companyName = row.companyName,
    s.phone = row.phone;
```

**Load Regions:**
```cypher
LOAD CSV WITH HEADERS FROM "file:///regions.csv" AS row
MERGE (r:Region {regionID: toInteger(row.regionID)})
SET r.regionDescription = row.regionDescription;
```

**Load Territories:**
```cypher
LOAD CSV WITH HEADERS FROM "file:///territories.csv" AS row
MERGE (t:Territory {territoryID: row.territoryID})
SET t.territoryDescription = row.territoryDescription;
```

**Load Orders:**
```cypher
LOAD CSV WITH HEADERS FROM "file:///orders.csv" AS row
MERGE (o:Order {orderID: toInteger(row.orderID)})
SET o.orderDate = row.orderDate,
    o.requiredDate = row.requiredDate,
    o.shippedDate = row.shippedDate,
    o.freight = toFloat(row.freight),
    o.shipName = row.shipName,
    o.shipAddress = row.shipAddress,
    o.shipCity = row.shipCity,
    o.shipRegion = row.shipRegion,
    o.shipPostalCode = row.shipPostalCode,
    o.shipCountry = row.shipCountry;
```
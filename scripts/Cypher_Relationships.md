## Create Relationships

**Product → Category (PART_OF):**
```cypher
LOAD CSV WITH HEADERS FROM "file:///products.csv" AS row
MATCH (p:Product {productID: toInteger(row.productID)})
MATCH (c:Category {categoryID: toInteger(row.categoryID)})
MERGE (p)-[:PART_OF]->(c);
```

**Supplier → Product (SUPPLIES):**
```cypher
LOAD CSV WITH HEADERS FROM "file:///products.csv" AS row
MATCH (p:Product {productID: toInteger(row.productID)})
MATCH (s:Supplier {supplierID: toInteger(row.supplierID)})
MERGE (s)-[:SUPPLIES]->(p);
```

**Customer → Order (PURCHASED):**
```cypher
LOAD CSV WITH HEADERS FROM "file:///orders.csv" AS row
MATCH (c:Customer {customerID: row.customerID})
MATCH (o:Order {orderID: toInteger(row.orderID)})
MERGE (c)-[:PURCHASED]->(o);
```

**Employee → Order (SOLD):**
```cypher
LOAD CSV WITH HEADERS FROM "file:///orders.csv" AS row
MATCH (e:Employee {employeeID: toInteger(row.employeeID)})
MATCH (o:Order {orderID: toInteger(row.orderID)})
MERGE (e)-[:SOLD]->(o);
```

**Order → Product (ORDERS) with details:**
```cypher
LOAD CSV WITH HEADERS FROM "file:///order-details.csv" AS row
MATCH (o:Order {orderID: toInteger(row.orderID)})
MATCH (p:Product {productID: toInteger(row.productID)})
MERGE (o)-[rel:ORDERS]->(p)
SET rel.unitPrice = toFloat(row.unitPrice),
    rel.quantity = toInteger(row.quantity),
    rel.discount = toFloat(row.discount);
```

**Order → Shipper (SHIPPED_BY):**
```cypher
LOAD CSV WITH HEADERS FROM "file:///orders.csv" AS row
MATCH (o:Order {orderID: toInteger(row.orderID)})
MATCH (s:Shipper {shipperID: toInteger(row.shipVia)})
MERGE (o)-[:SHIPPED_BY]->(s);
```

**Employee → Employee (REPORTS_TO):**
```cypher
LOAD CSV WITH HEADERS FROM "file:///employees.csv" AS row
WITH row WHERE row.reportsTo IS NOT NULL AND row.reportsTo <> "NULL"
MATCH (e:Employee {employeeID: toInteger(row.employeeID)})
MATCH (m:Employee {employeeID: toInteger(row.reportsTo)})
MERGE (e)-[:REPORTS_TO]->(m);
```

**Territory → Region (IN_REGION):**
```cypher
LOAD CSV WITH HEADERS FROM "file:///territories.csv" AS row
MATCH (t:Territory {territoryID: row.territoryID})
MATCH (r:Region {regionID: toInteger(row.regionID)})
MERGE (t)-[:IN_REGION]->(r);
```

**Employee → Territory (IN_TERRITORY):**
```cypher
LOAD CSV WITH HEADERS FROM "file:///employee-territories.csv" AS row
MATCH (e:Employee {employeeID: toInteger(row.employeeID)})
MATCH (t:Territory {territoryID: row.territoryID})
MERGE (e)-[:IN_TERRITORY]->(t);
```
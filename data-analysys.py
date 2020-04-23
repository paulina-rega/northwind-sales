import pandas as pd
from matplotlib import pyplot as plt

df_categories = pd.read_csv('categories.csv')
df_categories.drop('picture', axis = 1, inplace = True)


df_customers = pd.read_csv('customers.csv')
df_customers.drop(['region', 'postalCode', 'phone', 'fax', 
                   'contactTitle', 'contactName', 'address'], 
                  axis = 1, inplace = True)
df_customers.rename(columns = {'companyName': 'customerCompanyName',
                               'city': 'customerCity',
                               'country': 'customerCountry'}, inplace = True)


df_orders = pd.read_csv('orders.csv')
df_orders.drop(['shipRegion', 'shipAddress', 'shipPostalCode', 'shipName'],
               axis = 1, inplace = True)



df_order_detail = pd.read_csv('order_details.csv')

df_products = pd.read_csv('products.csv')
df_products.drop(['quantityPerUnit', 'unitPrice', 'unitsInStock', 
                  'unitsOnOrder', 'reorderLevel', 'discontinued'], axis = 1, 
                 inplace = True)

df_categories = pd.read_csv('categories.csv')
df_categories.drop(['picture', 'description'], axis = 1, inplace = True)


df_suppliers = pd.read_csv('suppliers.csv')
df_suppliers.drop(['contactName', 'contactTitle', 'address', 'city', 
                   'region', 'postalCode', 'country', 'phone', 'fax',
                   'homePage'], axis = 1, inplace = True)
df_suppliers.rename(columns = {'companyName': 'supplierCompanyName'},
                    inplace = True)



df_employees = pd.read_csv('employees.csv')
df_employees.drop(['postalCode', 'homePhone', 'extension',
                   'photo', 'notes', 'photoPath', 'birthDate', 'hireDate',
                   'address', 'city', 'reportsTo'], axis = 1, inplace = True)
df_employees.rename(columns = {'lastName': 'employeeLastName',
                               'firstName' : 'employeeFirstName',
                               'title': 'employeeTitle',
                               'titleOfCourtesy': 'employeeTitleOfCourtesy',
                               'country': 'employeeCountry'}, inplace = True)



df_shippers = pd.read_csv('shippers.csv')
df_shippers.drop('phone', axis = 1, inplace = True)
df_shippers.rename(columns = {'companyName': 'shipperCompanyName'},
                 inplace = True)


df = df_suppliers.merge(df_products, on = 'supplierID')
df = df.merge(df_categories, on = 'categoryID')
df = df.merge(df_order_detail, on = 'productID')
df = df.merge(df_orders, on = 'orderID')
df = df.merge(df_customers, on = 'customerID')
df = df.merge(df_shippers, left_on = 'shipVia', right_on = 'shipperID', 
              how = 'inner')
df = df.merge(df_employees, on = 'employeeID')

df.drop(['supplierID', 'productID', 'customerID', 'employeeID'], axis = 1, inplace = True)


# szukanie najlepiej sprzedających się produktów:

top_products_sales = list(df.groupby('productName').sum().sort_values(
    by = 'quantity', ascending = False).head(5).index)

top_categories_sales = []
for prod in top_products_sales:
    category_id = df_products[df_products['productName'] == prod]['categoryID'].tolist()[0]
    category_name = df_categories[df_categories['categoryID'] == category_id]['categoryName'].tolist()[0]
    top_categories_sales.append(category_name)
    
top_categories_sales = list(set(top_categories_sales))


print('Most popular categories: ')
for i in top_categories_sales:
    print("\t- "+i)
print('\n')



# dodanie kolumny z wartością sprzedanych produktów 

df['totalValue'] = (df['unitPrice'] - df['unitPrice'] * df['discount']) * \
    df['quantity']
    
    
# 5 klientów, któ®zy kupili najwięcej produktów

top_clients = list(df.groupby('customerCompanyName').sum().sort_values(
    by = 'quantity', ascending = False).head(5).index)

print('Top clients: ')
for i in top_clients:
    print("\t- "+i)
print('\n')



# histogram obrazujący 5 państw z największą liczbą transakcji


top_countries_by_transaction = df.groupby(
    'customerCountry')['orderID'].nunique().sort_values(
        ascending = False).head(5)


top_countries_by_transaction_x = list(top_countries_by_transaction.index)
top_countries_by_transaction_y = top_countries_by_transaction.tolist()

plt.bar(top_countries_by_transaction_x, top_countries_by_transaction_y)
plt.title('Top countries by transactions')
plt.ylabel('No of transaction')
plt.show()

# histogram obrazujący 5 państw z największą wartością transakcji

top_countries_by_value = df.groupby('customerCountry').sum().sort_values(
    by = 'totalValue', ascending = False).head(5)

top_countries_by_value_x = list(top_countries_by_value.index)
top_countries_by_value_y = top_countries_by_value['totalValue'].tolist()

plt.bar(top_countries_by_value_x, top_countries_by_value_y)
plt.title('Top countries by value')
plt.ylabel('Total value of transactions')
plt.show()

# który region sprzedał najwięcej / największą wartość – za mało danych

# ilość unikalnych klientów sklepu
unique_customers = df['customerCompanyName'].nunique()
print('Number of uniques customers: {}\n'.format(unique_customers))


# dostawca od którego kupowane są najdroższe produkty 

supplier = df.groupby('supplierCompanyName')['unitPrice'].sum() / df.groupby('supplierCompanyName')['quantity'].sum()


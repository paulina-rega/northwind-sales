import pandas as pd
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans

# loading and deleting unuesful data:

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
df_products.drop(['quantityPerUnit', 'unitPrice', 
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

df.drop(['supplierID', 'productID', 'customerID', 'employeeID'], axis = 1, 
        inplace = True)

df['totalValue'] = (df['unitPrice'] - df['unitPrice'] * df['discount']) * \
    df['quantity']


# finding most popular products categories (by quantity):

top_products_sales = list(df.groupby('productName').sum().sort_values(
    by = 'quantity', ascending = False).head(5).index)

top_categories_sales = []
for prod in top_products_sales:
    category_id = (df_products[df_products['productName'] == prod]
                   ['categoryID'].tolist()[0])
    category_name = (df_categories[df_categories['categoryID'] == category_id]
                     ['categoryName'].tolist()[0])
    top_categories_sales.append(category_name)
    
top_categories_sales = list(set(top_categories_sales))


print('Most popular categories: ')
for i in top_categories_sales:
    print("\t- "+i)
print('\n')

    
# finding top 5 clients (by quantity):

top_clients = list(df.groupby('customerCompanyName').sum().sort_values(
    by = 'quantity', ascending = False).head(5).index)

print('Top clients: ')
for i in top_clients:
    print("\t- "+i)
print('\n')



# creating plot with top 5 countries (by amount of transactions):


top_countries_by_transaction = df.groupby(
    'customerCountry')['orderID'].nunique().sort_values(
        ascending = False).head(5)


top_countries_by_transaction_x = list(top_countries_by_transaction.index)
top_countries_by_transaction_y = top_countries_by_transaction.tolist()

plt.bar(top_countries_by_transaction_x, top_countries_by_transaction_y)
plt.title('Top countries by transactions')
plt.ylabel('No of transaction')
plt.show()

# creating plot with top 5 countries (by total value of transactions):

top_countries_by_value = df.groupby('customerCountry').sum().sort_values(
    by = 'totalValue', ascending = False).head(5)

top_countries_by_value_x = list(top_countries_by_value.index)
top_countries_by_value_y = top_countries_by_value['totalValue'].tolist()

plt.bar(top_countries_by_value_x, top_countries_by_value_y)
plt.title('Top countries by value')
plt.ylabel('Total value of transactions')
plt.show()


# calculating number of unique customers

unique_customers = df['customerCompanyName'].nunique()
print('Number of unique customers: {}\n'.format(unique_customers))


# findind suppliers with the most valuable products (by price):

most_val_prods_supplier = df.groupby('supplierCompanyName')['unitPrice'].sum(
    ) / df.groupby('supplierCompanyName')['quantity'].sum()
most_val_prods_supplier = most_val_prods_supplier.head(1).index[0]

print('Supplier providing the most valuable products: {}.\n'.format(
    most_val_prods_supplier))


# finding suppliers delivering highest amount of products:

suppliers_by_amount = df.groupby('supplierCompanyName')['unitsInStock'].count()
top_supplier = suppliers_by_amount.sort_values(ascending = False).index[0]
print('Supplier from whom the store buys the most products: {}.\n'.format(
    top_supplier))



# Market segmentation - customers types:

customers_by_mean_value = df.groupby('customerCompanyName').sum().sort_values(
    by = 'totalValue', ascending = False)
customers_by_mean_value = (customers_by_mean_value['totalValue']
                           /customers_by_mean_value['quantity'].sort_index())

customers_by_amount = df.groupby('customerCompanyName').sum().sort_values(
    by = 'quantity', ascending = False)['quantity'].sort_index()




x = customers_by_mean_value.tolist()
y = customers_by_amount.tolist()
df_k_means = pd.DataFrame({'meanValue': customers_by_mean_value, 
                           'quantity': customers_by_amount})
'''
#this code block was used to determine optimal number of segments

plt.plot(x, y, 'ob')
plt.show()


inertia = []
for i in range(1,10):
    kmeans = KMeans(n_clusters = i, max_iter = 100, n_init = 10, 
                     random_state = 0)
    kmeans.fit(df_k_means)
    inertia.append(kmeans.inertia_)
    
plt.plot(inertia)
plt.show()
'''

clusters_n = 2
kmeans = KMeans(n_clusters = clusters_n, max_iter = 10, n_init = 10, 
                random_state = 0)
y_means = kmeans.fit_predict(df_k_means)

k_plot = plt.scatter(x, y, c = y_means)


plt.xlabel('Mean value of bought products')
plt.ylabel('Amount of products')
plt.title('Customers segments by value and quantity of products')

plt.text(30, 4500, "customers buying basic products", color = "orange", 
         weight = 'normal')
plt.text(40, 1100, "average customers", color = "midnightblue", 
         weight = 'normal')
plt.show()


# Market segmentation - countries types:
    
countries_by_mean_value = df.groupby('customerCountry').sum().sort_values(
    by = 'totalValue', ascending = False)
countries_by_mean_value = (countries_by_mean_value['totalValue']
                           /countries_by_mean_value['quantity'].sort_index())

countries_by_amount = df.groupby('customerCountry').sum().sort_values(
    by = 'quantity', ascending = False)['quantity'].sort_index()



x = countries_by_mean_value.tolist()
y = countries_by_amount.tolist()
df_k_means = pd.DataFrame({'meanValue': countries_by_mean_value, 
                           'quantity': countries_by_amount})



'''
#this code block was used to determine optimal number of segments

plt.plot(x, y, 'ob')
plt.show()
inertia = []
for i in range(1,10):
    kmeans = KMeans(n_clusters = i, max_iter = 100, n_init = 10, 
                     random_state = 0)
    kmeans.fit(df_k_means)
    inertia.append(kmeans.inertia_)
    
plt.plot(inertia)
plt.show()
'''


clusters_n = 2
kmeans = KMeans(n_clusters = clusters_n, max_iter = 10, n_init = 10, 
                random_state = 0)
y_means = kmeans.fit_predict(df_k_means)

k_plot = plt.scatter(x, y, c = y_means)


plt.xlabel('Mean value of bought products')
plt.ylabel('Amount of products')
plt.title('Countries segments by value and quantity of products')

plt.text(20, 7000, "valuable and stable markets", color = "orange", 
         weight = 'normal')
plt.text(27, 3100, "average markets", color = "midnightblue", 
         weight = 'normal')


plt.show()



# Products recommendation:
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

df_apriori = df[['orderID','productName']]
df_apriori = pd.concat([df_apriori, pd.get_dummies(df_apriori['productName'], 
                                                   prefix="")], axis=1)
df_apriori.drop(['productName'], axis = 1, inplace = True)



df_apriori = df_apriori.groupby('orderID').sum()
df_apriori = (df_apriori/df_apriori).fillna(0)


frequent_items = apriori(df_apriori, min_support=0.003, use_colnames = True)
rules = association_rules(frequent_items, metric = 'lift', min_threshold = 1)
result = rules.sort_values(['confidence'],  ascending = [0]).head(10)

print('Products that could be recommended when one in pair is to be bought')
print(result.loc[:, ['antecedents', 'consequents']])
print('\n')



# Categories of products recommendation:
df_apriori = df[['orderID','categoryName']]
df_apriori = pd.concat([df_apriori, pd.get_dummies(df_apriori['categoryName'],
                                                   prefix="")], axis=1)
df_apriori.drop(['categoryName'], axis = 1, inplace = True)



df_apriori = df_apriori.groupby('orderID').sum()
df_apriori = (df_apriori/df_apriori).fillna(0)


frequent_items = apriori(df_apriori, min_support=0.005, use_colnames = True)
rules2 = association_rules(frequent_items, metric = 'lift', min_threshold = 1)
result2 = rules2.sort_values(['lift'],  ascending = [0]).head(3)


print('Categories that goes together:')
print(result2.loc[:, ['antecedents', 'consequents']])
print('\n')

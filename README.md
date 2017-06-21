# Item Catalog Application

Application provides a list of items according to their catalog information. Edit, add and delete functions for registered users.

## How to run

You can create sample data by using  "python add_data_script.py" command

You can start application by using "python project.py" command

## Usage

* Main page(List categories and latest items) -> http://localhost:5000/catalog/ 

* Category page(Can be accessed from main page) -> http://localhost:5000/catalog/[Category_name]/items/

* Item Page(Can be accessed from main page and category page) -> http://localhost:5000/catalog/[Category_name]/[Item_title]/

* You should login to add, update and delete item. You can only update and delete items those are created by you.

* Add item page -> http://localhost:5000/item/new/

* Edit item page(Can be accessed from item page) -> http://localhost:5000/catalog/[Category_name]/[Item_title]/edit

* Delete item page(Can be accessed from item page) -> http://localhost:5000/catalog/[Category_name]/[Item_title]/delete

* In order to get catalog data as json -> http://localhost:5000/catalog.json


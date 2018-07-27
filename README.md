# MedTech

Requirements:
1) Django 2.0.7
2) djangorestframework
3) psycopg2
4) requests

DB: PostgreSQL
Python: 3.6


В проекте не работает пролистывание страниц таблицы при включенном фильтре. Это фиксится добавлением javascript-ов для каждой из ссылок пролистывания (парсинг GET параметров, и добавление/обновление page=.. без удаление других параметров). К сожалению, у меня не хватило на это времени.

"Внешний сервис" реализован в функции: contacts.utils.import_contacts(), но не добавлен  ни в один из запросов.

Фильтры для задания "Иерархическая структура" реализованы в contacts.utils.filter_by_word() и contacts.utils.filter_can_have_word(). Первый из них изет вхождение подстроки, второй - учитывает компании с неполными адресами.


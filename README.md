# Yatube 

Социальная сеть Yatube даёт пользователям возможность совершать CRUD операции со своими постами и комментариями, учётной записью; позволяет просматривать ленту, отмечать понравившиеся записи и подписываться на других авторов.

<details>
   <summary>Материалы от заказчика</summary> 
  
Необходимо разработать социальную сеть для публикации личных дневников. 
Это будет сайт, на котором можно создать свою страницу. Если на нее зайти, то можно посмотреть все записи автора.
Пользователи смогут заходить на чужие страницы, подписываться на авторов и комментировать их записи. 
Автор может выбрать имя и уникальный адрес для своей страницы. 
Дизайн можно взять самый обычный, но красивый.
Еще надо иметь возможность модерировать записи и блокировать пользователей, если начнут присылать спам.
Записи можно отправить в сообщество и посмотреть там записи разных авторов.
Вы же программисты, сами понимаете, как лучше сделать.
</details>

<details>
   <summary>Что было сделано</summary> 
  
- создан Django-проект
- настроена админ-зона
- настроен рендеринг HTML-шаблонов
- подключён CSS
- осуществлено взаимодействие Django с БД SQLite посредством Django ORM
- настроена пагинация с помощью стандартного модуля Paginator
- осуществлена кастомизация страниц стандартных ошибок
- осуществлено кеширование главной страницы с помощью бэкенда LocMemCache
- код покрыт тестами, написанными с использованием библиотеки Unittest
</details>

<details>
   <summary>Запуск проекта в dev-режиме</summary> 

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:kkhitalenko/Yatube.git
```

```
cd Yatube/
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:
```
cd yatube/
```

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
</details>

## Используемые технологиии:

<div>
  <img src="https://github.com/devicons/devicon/blob/master/icons/python/python-original-wordmark.svg" title="Python" alt="Python" width="40" height="40"/>&nbsp;
  <img src="https://github.com/devicons/devicon/blob/master/icons/django/django-plain.svg" title="Django" alt="Django" width="40" height="40"/>&nbsp;
  <img src="https://github.com/devicons/devicon/blob/master/icons/sqlite/sqlite-original.svg" title="SQLite" alt="SQLite" width="40" height="40"/>&nbsp;
</div>
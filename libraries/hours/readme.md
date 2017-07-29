# Open Hours

This app provides a way to manage our open hours as data, present it as content, and provide a JSON API so our external services can also detect if we're open or closed.

## API

The API endpoint is `/hours/`. Its parameters are:

- `format`: this should always be set to `json`, otherwise requests will be redirect to the hours web page. We may add other formats if the need arises.
- `library` (optional): set to one of the library branches to receive its open hours for the current time period
- `date` (optional): set to a particular date (ISO format 'YYYY-MM-DD') to receive the times that each library is open on that date

If neither a `library` nor `date` is provided, then the results for the present `date` are returned. Also, `library` and `date` cannot be combined; if you provide both, the results for the identical `library` request will be returned. In the future, I hope to add functionality such that both parameters can be combined.

Example in JavaScript:

```js
let day = '2017-07-07'
// add the domain obviously, e.g. http://libraries.cca.edu
let url = `/hours/?format=json&date=${day}`
fetch(url)
    .then(res => res.json())
    .then(hours => console.log(hours))
```

## Data Model

There are three models that form the hours app: Library, OpenHours, and Closures.

The **Library** model represents a single library location with an independent set of open hours. Right now, it is only a name but in the future we add additional metadata such as contact information or street address.

The **OpenHours** model represents the regular open hours during a week for a particular library during a time period. So, for instance, an OpenHours instance could be described as "**Meyer** Library is open from 9am - 5pm Monday through Friday, and closed on Saturday and Sunday, for the dates of June 1st, 2017 to August 1st, 2017."

The **Closures** model represents _exceptions_ inside an OpenHours instance wherein a library is closed when it wouldo otherwise be open. Holidays are a prime example; while Meyer might be open on weekdays during the summer, we would add a closure instance for July 4th. Closures greatly reduce the number of OpenHours instances we need to create (otherwise they'd triple; one for the period before a holiday, one for the holiday, and one for the time after).

Right now, the OpenHours model has seven attributes, one for each weekday, all of which are named with the lowercase first three letters of the English name of the weekday, e.g. "mon", "tue". The data contained in the attribute is a string _with no restrictions_ placed upon it except length. This means the string could be "closed" or a range of hours. For our purposes, we should restrict these text strings to the following forms:

- #am - #pm
- closed

where "#" is one or two digits.

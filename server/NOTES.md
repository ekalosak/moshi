# Developer notes

## Including javascript
[StackOverflow](https://stackoverflow.com/questions/30011170/flask-application-how-to-link-a-javascript-file-to-website)
shows that you put in `static/` as a sister to `template/` and then:
```html
<script src="{{url_for('static', filename='somejavascriptfile.js')}}"></script>
```

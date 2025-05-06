from flask import Flask, render_template, request, redirect, url_for
from jinja2 import DictLoader
import os

# Create Flask app, serve static files
app = Flask(__name__, static_folder='static')

# --- local dataset ---
def load_local_dataset():
    # First movie, id=0
    initial = [{
        "id": 0,
        "title": "Transformers: Dark of the Moon",
        "director": "Michael Bay",
        "year": 2011,
        "cast": ["Shia LaBeouf", "Rosie Huntington-Whiteley", "Tyrese Gibson"],
        "summary": (
            "Sam Witwicky (Shia LaBeouf) and his new girlfriend, Carly (Rosie Huntington-Whiteley), "
            "join the fray when the evil Decepticons renew their longstanding war against the Autobots. "
            "Optimus Prime (Peter Cullen) believes that resurrecting ancient Transformer Sentinel Prime "
            "(Leonard Nimoy), once the leader of the Autobots, may lead to victory. That decision, however, "
            "has devastating consequences; the war appears to tip in favor of the Decepticons, leading to a "
            "climactic battle in Chicago."
        )
    }]
    # Remaining movies, starting from id=1
    others = []
    movies = [
        ("Transformers One", "Josh Cooley", 2024,
         ["Chris Hemsworth", "Brian Tyree Henry", "Scarlett Johansson"],
         "Once upon a time, Optimus Prime and Megatron were friends bonded like brothers who managed to change the "
         "fate of the Cybertron planet forever. This is their untold original story, before they end up being bitter "
         "opponents."),
        ("Avengers: Infinity War", "Anthony Russo, Joe Russo", 2018,
         ["Robert Downey Jr.", "Chris Evans", "Mark Ruffalo"],
         "Iron Man, Thor, the Hulk and the rest of the Avengers unite to battle their most powerful enemy yet "
         "-- the evil Thanos. On a mission to collect all six Infinity Stones, Thanos plans to use the artifacts "
         "to inflict his twisted will on reality. The fate of the planet and existence itself has never been more "
         "uncertain as everything the Avengers have fought for has led up to this moment."),
        ("Avengers: Endgame", "Anthony Russo, Joe Russo", 2019,
         ["Robert Downey Jr.", "Chris Evans", "Mark Ruffalo, Chris Hemsworth"],
         "The fourth installment in the Avengers saga is the culmination of 22 interconnected Marvel films and the "
         "climax of a journey. The world's heroes finally understand just how fragile reality is, and the sacrifices "
         "that must be made to uphold it, in a story of friendship, teamwork and setting aside differences to overcome "
         "an impossible obstacle."),
        ("How to Train Your Dragon", "Dean DeBlois", 2010,
         ["Jay Baruchel", "Gerard Butler", "America Ferrera"],
         "Hiccup (Chris Sanders) is a Norse teenager from the island of Berk, where fighting dragons is a way of life. "
         "His progressive views and weird sense of humor make him a misfit, despite the fact that his father (Dean DeBlois) "
         "is chief of the clan."),
        ("How to Train Your Dragon 2", "Dean DeBlois", 2014,
         ["Jay Baruchel", "Gerard Butler", "Cate Blanchett"],
         "Five years have passed since Hiccup and Toothless united the dragons and Vikings of Berk. Now, they "
         "spend their time charting the island's unmapped territories. During one of their adventures, the pair "
         "discover a secret cave that houses hundreds of wild dragons -- and a mysterious dragon rider who turns "
         "out to be Hiccup's long-lost mother, Valka (Cate Blanchett). Hiccup and Toothless then find themselves "
         "at the center of a battle to protect Berk from a power-hungry warrior named Drago."),
        ("Oppenheimer", "Christopher Nolan", 2024,
         ["Cillian Murphy", "Florence Pugh", "Emily Blunt", "Josh Hartnett"],
         "During World War II, Lt. Gen. Leslie Groves Jr. appoints physicist J. Robert Oppenheimer to work on "
         "the top-secret Manhattan Project. Oppenheimer and a team of scientists spend years developing and designing "
         "the atomic bomb. Their work comes to fruition on July 16, 1945, as they witness the world's first nuclear "
         "explosion, forever changing the course of history."),
        ("Barbie", "Greta Gerwig", 2023,
         ["Margot Robbie", "Ryan Gosling", "America Ferrera"],
         "Barbie and Ken are having the time of their lives in the colorful and seemingly perfect world of Barbie "
         "Land. However, when they get a chance to go to the real world, they soon discover the joys and perils of "
         "living among humans.")
    ]
    for idx, (title, director, year, cast, summary) in enumerate(movies, start=1):
        others.append({
            "id": idx,
            "title": title,
            "director": director,
            "year": year,
            "cast": cast,
            "summary": summary,
        })
    return initial + others

# Initialize dataset and catalog
dataset = load_local_dataset()
catalog = set()

# --- Templates stored in mem ---
templates = {
    'base.html': '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>My Movie Catalog</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
  </head>
  <body>
    <h1>My Movie Catalog</h1>
    <nav>
      <a href="{{ url_for('home') }}">Home</a> |
      <a href="{{ url_for('search') }}">Search</a> |
      <a href="{{ url_for('view_catalog') }}">Catalog</a> |
      <a href="{{ url_for('add_movie') }}">Add Movie</a>
    </nav>
    <hr>
    {% block body %}{% endblock %}

    <!-- Confirmation Modal -->
    <div id="confirmModal" class="modal">
      <div class="modal-content confirm">
        <p id="confirm-text">Are you sure?</p>
        <div class="confirm-buttons">
          <button id="confirm-yes">Yes</button>
          <button onclick="closeConfirm()">No</button>
        </div>
      </div>
    </div>

    <script>
      let confirmURL = "";
      function openConfirm(msg, url) {
        document.getElementById("confirm-text").textContent = msg;
        confirmURL = url;
        document.getElementById("confirmModal").style.display = "block";
      }
      function closeConfirm() {
        document.getElementById("confirmModal").style.display = "none";
      }
      document.getElementById("confirm-yes")
        .addEventListener("click", () => {
          closeConfirm();
          window.location.href = confirmURL;
        });
      window.onclick = e => {
        if (e.target === document.getElementById("confirmModal")) {
          closeConfirm();
        }
      };
    </script>
  </body>
</html>''',

    'welcome.html': '''{% extends "base.html" %}
{% block body %}
  <div class="welcome-container">
    <h2>Welcome!</h2>
    <form action="{{ url_for('home') }}" method="get">
      <button type="submit" class="start-btn">Start</button>
    </form>
    <p class="page-instruction">
      Keep track of movies you have watched in your own movie catalog!  
      Search for more movies to watch!
    </p>
  </div>
{% endblock %}''',

    'home.html': '''{% extends "base.html" %}
{% block body %}
<h2>Homepage</h2>
<ul>
  <li><a href="{{ url_for('search') }}">Search for Movies</a></li>
  <li><a href="{{ url_for('view_catalog') }}">View Your Catalog</a></li>
  <li><a href="{{ url_for('add_movie') }}">Add New Movie</a></li>
</ul>
{% endblock %}''',

'search.html': '''
<!-- search.html -->
{% extends "base.html" %}
{% block body %}
  <h2>Search Movies</h2>
  <p class="page-instruction">
    Enter a title or keyword below and hit “Search” to find movies.
  </p>
  <form method="post">
    <input name="query" placeholder="Enter keyword"
           value="{{ query|default('') }}">
    <button type="submit">Search</button>
  </form>
  <ul>
    {% for m in results %}
      <li>{{ m.title }}
        {% if m.id in catalog %}
          <a href="#"
             onclick="
               openConfirm(
                 'Are you sure you want to remove this movie from your catalog?',
                 '{{ url_for('toggle', movie_id=m.id, back='search') }}'
               );
               return false;
             ">
            Remove
          </a>
        {% else %}
          [<a href="{{ url_for('toggle', movie_id=m.id, back='search') }}">Add</a>]
        {% endif %}
        – <a href="{{ url_for('detail', movie_id=m.id) }}">Details</a>
      </li>
    {% endfor %}
  </ul>
{% endblock %}''',

    'catalog.html': '''
<!-- catalog.html -->
{% extends "base.html" %}
{% block body %}
  <h2>My Catalog</h2>
  <p class="page-instruction">
    Welcome to your personal catalog, here are the movies you’ve watched, click “Details” to 
    get more details on movies or click “Remove” to remove a movie from your catalog.
  </p>
  <ul>
    {% for m in catalog_movies %}
      <li>{{ m.title }}
        <a href="#"
           onclick="
             openConfirm(
               'Are you sure you want to remove this movie from your catalog?',
               '{{ url_for('toggle', movie_id=m.id, back='catalog') }}'
             );
             return false;
           ">
          Remove
        </a>
        – <a href="{{ url_for('detail', movie_id=m.id) }}">Details</a>
      </li>
    {% endfor %}
  </ul>
{% endblock %}''',

    'detail.html': '''
<!-- detail.html -->
{% extends "base.html" %}
{% block body %}
  <h2>{{ movie.title }} ({{ movie.year }})</h2>
  <p><strong>Director:</strong> {{ movie.director }}</p>
  <p><strong>Cast:</strong> {{ movie.cast|join(', ') }}</p>
  <p><strong>Summary:</strong> {{ movie.summary }}</p>
  <p>
    {% if movie.id in catalog %}
      <a href="#"
         onclick="
           openConfirm(
             'Are you sure you want to remove this movie from your catalog?',
             '{{ url_for('toggle', movie_id=movie.id, back='detail', id=movie.id) }}'
           );
           return false;
         ">
        Remove
      </a>
    {% else %}
      <a href="{{ url_for('toggle', movie_id=movie.id, back='detail', id=movie.id) }}">Add</a>
    {% endif %}
  </p>
{% endblock %}''',

    'add.html': '''{% extends "base.html" %}
{% block body %}
<h2>Add New Movie</h2>
  <p class="page-instruction">
    Fill out the form below to add a new movie to the database.
  </p>
<form method="post" action="{{ url_for('add_movie') }}">
  <p>
    <label>Title:<br>
      <input type="text" name="title" required>
    </label>
  </p>
  <p>
    <label>Director:<br>
      <input type="text" name="director" required>
    </label>
  </p>
  <p>
    <label>Year:<br>
      <input type="number" name="year" min="1888" max="2100" required>
    </label>
  </p>
  <p>
    <label>Cast (comma-separated):<br>
      <input type="text" name="cast">
    </label>
  </p>
  <p>
    <label>Summary:<br>
      <textarea name="summary" rows="4"></textarea>
    </label>
  </p>
  <button type="submit">Add Movie</button>
</form>
{% endblock %}''' 
}

# Configure Jinja loader
app.jinja_loader = DictLoader(templates)

# --- Route definitions ---
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/search', methods=['GET','POST'])
def search():
    query = request.form.get('query','') if request.method == 'POST' else ''
    results = [m for m in dataset if query.lower() in m['title'].lower()]
    return render_template('search.html', results=results, catalog=catalog, query=query)

@app.route('/catalog')
def view_catalog():
    catalog_movies = [m for m in dataset if m['id'] in catalog]
    return render_template('catalog.html', catalog_movies=catalog_movies, catalog=catalog)

@app.route('/detail/<int:movie_id>')
def detail(movie_id):
    movie = next(m for m in dataset if m['id'] == movie_id)
    return render_template('detail.html', movie=movie, catalog=catalog)

@app.route('/add', methods=['GET','POST'])
def add_movie():
    if request.method == 'POST':
        # Extract form data
        title    = request.form['title']
        director = request.form['director']
        year     = int(request.form['year'])
        cast_list = request.form.get('cast','').split(',')
        cast     = [c.strip() for c in cast_list if c.strip()]
        summary  = request.form.get('summary','')
        # Assign a new unique ID
        new_id = max(m['id'] for m in dataset) + 1
        # Append to dataset
        dataset.append({
            'id': new_id,
            'title': title,
            'director': director,
            'year': year,
            'cast': cast,
            'summary': summary
        })
        # Redirect to detail page
        return redirect(url_for('detail', movie_id=new_id))
    # show the empty form
    return render_template('add.html')

@app.route('/toggle/<int:movie_id>')
def toggle(movie_id):
    back = request.args.get('back','home')
    if movie_id in catalog:
        catalog.remove(movie_id)
    else:
        catalog.add(movie_id)
    if back == 'search': return redirect(url_for('search'))
    if back == 'catalog': return redirect(url_for('view_catalog'))
    if back == 'detail': return redirect(url_for('detail', movie_id=request.args.get('id')))
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
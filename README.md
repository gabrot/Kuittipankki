# Kuittipankki

Kuittipankki on kuittienhallintasovellus, joka on rakennettu Flask'n avulla. Sovellus mahdollistaa kuittien hallinnan, seurannan ja analysoinnin sekä saada yleiskuvan kulutustottumuksistasi.

## Ominaisuudet

- Kuittien lisääminen ja hallinta
- Kuittien kuvien tallennus ja tarkastelu
- Kategorioiden ja summien analysointi

## Sovelluksen tila

Sovellus on tällä hetkellä varhaisessa kehitysvaiheessa. Seuraavat ominaisuudet on toteutettu:
- PostgreSQL-tietokanta on integroitu sovellukseen.
- Perustoiminnallisuudet kuittien lisäämiseksi tietokantaan on luotu.
- Käyttäjien rekisteröinti ja kirjautuminen on mahdollista.

Seuraavaksi kehitetään käyttöliittymä, joka mahdollistaa kuittien hallinnan ja lisäämisen tietokantaan.

## Asennusohjeet

1. **Kloonaa repositorio:**

    ```bash
    git clone https://github.com/gabrot/kuittipankki.git
    cd kuittipankki
    ```

2. **Luo ja aktivoi virtuaaliympäristö:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate  # Windows
    ```

3. **Asenna riippuvuudet:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Asenna ja käynnistä PostgreSQL**

    ### Ubuntu/Debian
    ```sh
    sudo apt update
    sudo apt install postgresql postgresql-contrib
    sudo service postgresql start
    ```

    ### macOS (Homebrew)
    ```sh
    brew install postgresql
    brew services start postgresql
    ```

    ### Windows
    1. Lataa ja asenna PostgreSQL [PostgreSQL Download](https://www.postgresql.org/download/windows/).
    2. Käynnistä PostgreSQL-palvelin PostgreSQL Shell (psql) -sovelluksella tai Windows-palveluista.

5. **Luo uusi käyttäjä ja tietokanta PostgreSQL:ssä**

    ```sh
    psql -U postgres
    ```

    ```sql
    CREATE USER johndoe WITH PASSWORD 'mysecretpassword';
    CREATE DATABASE kuittipankki;
    GRANT ALL PRIVILEGES ON DATABASE kuittipankki TO johndoe;
    ```

6. **Määritä ympäristömuuttujat:**

    Luo `.env`-tiedosto ja lisää seuraavat muuttujat:

    ```env
    FLASK_APP=app.py
    FLASK_ENV=development
    DATABASE_URL=postgresql://johndoe:mysecretpassword@localhost/kuittipankki
    SECRET_KEY=your_secret_key
    ```

    Muokkaa `DATABASE_URL` omien tietokanta-asetustesi mukaan.

7. **Alusta tietokanta:**

    ```bash
    flask db upgrade
    ```

8. **Käynnistä sovellus:**

    ```bash
    flask run
    ```

    Sovellus on nyt käynnissä oletusosoitteessa `http://127.0.0.1:5000/` tai omassa palvelinympäristössäsi määritetyssä osoitteessa.

## Testaus

Voit testata sovellusta paikallisesti seuraavien ohjeiden mukaisesti:

1. **Rekisteröidy ja kirjaudu sisään:**

    - Siirry osoitteeseen `http://127.0.0.1:5000/register` tai oman palvelimesi osoitteeseen ja luo uusi käyttäjätili.
    - Kirjaudu sisään luomallasi tunnuksella osoitteessa `http://127.0.0.1:5000/login` tai oman palvelimesi osoitteessa.

2. **Lisää uusi kuitti:**

    - Kirjautumisen jälkeen voit lisätä uuden kuitin siirtymällä osoitteeseen `/lisaa_kuitti`.
    - Täytä kuittilomake ja tallenna kuitti tietokantaan.

3. **Tarkastele kuittien listausta:**

    - Pääsivulla (`/`) voit tarkastella kaikkia lisättyjä kuitteja.

## Tulevat kehityssuunnitelmat

- Käyttöliittymän kehittäminen kuittien hallintaa varten.
- Parannettu virheenkäsittely ja käyttäjäkokemus.
- Mahdollisuus kuittien muokkaamiseen ja poistamiseen.
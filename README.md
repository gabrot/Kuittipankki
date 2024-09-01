# Kuittipankki

Kuittipankki on kuittienhallintasovellus, joka on rakennettu Flask'n avulla. Sovellus mahdollistaa kuittien hallinnan, seurannan ja analysoinnin sekä antaa yleiskuvan kulutustottumuksistasi.

## Ominaisuudet

- Käyttäjien rekisteröinti ja kirjautuminen
- Kuittien lisääminen, katselu ja poistaminen
- Kuittien kuvien tallennus ja tarkastelu
- Kuittien tallennus PostgreSQL-tietokantaan ilman ORM-työkaluja
- Kategorioiden, tagien, maksutapojen ja myyjien hallinta

## Sovelluksen tila

Sovellus on toiminnassa ja sisältää seuraavat ominaisuudet:
- PostgreSQL-tietokanta on integroitu sovellukseen.
- Kaikki tietokantakyselyt on kirjoitettu käsin ilman ORM-työkaluja.
- Käyttäjien rekisteröinti ja kirjautuminen toimii.
- Kuittien lisääminen, katselu ja poistaminen on mahdollista.
- Käyttäjät voivat hallita kategorioita, tageja, maksutapoja ja myyjiä.

Seuraavat ominaisuudet eivät ole vielä toteutettu:
- Kuittien muokkaaminen
- Yksityiskohtaiset raportit ja kulutusanalyysit
- Kuittien hakutoiminto

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
    brew install postgresql@14
    brew services start postgresql@14
    ```

    ### Windows
    1. Lataa ja asenna PostgreSQL [PostgreSQL Download](https://www.postgresql.org/download/windows/).
    2. Käynnistä PostgreSQL-palvelin PostgreSQL Shell (psql) -sovelluksella tai Windows-palveluista.

5. **Luo uusi käyttäjä ja tietokanta PostgreSQL:ssä**

    ```sh
    psql -U postgres
    ```

    ```sql
    CREATE USER your_database_username WITH PASSWORD 'your_database_password';
    CREATE DATABASE your_database_name;
    GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_database_username;
    ```

6. **Määritä ympäristömuuttujat:**

    Kopioi `.env.example`-tiedosto nimellä `.env` ja muokkaa sen sisältöä:

    ```bash
    cp .env.example .env
    ```

    Avaa `.env`-tiedosto ja muokkaa seuraavat muuttujat:

    ```env
    DB_NAME=your_database_name
    DB_USER=your_database_username
    DB_PASSWORD=your_database_password
    DB_HOST=localhost
    DB_PORT=5432
    SECRET_KEY=your_secret_key_here
    WTF_CSRF_SECRET_KEY=your_csrf_secret_key_here
    ```

    Korvaa `your_database_name`, `your_database_username`, ja `your_database_password` omilla tietokanta-asetuksillasi. Aseta myös `SECRET_KEY` ja `WTF_CSRF_SECRET_KEY` uniikkeihin, turvallisiin arvoihin.

7. **Alusta tietokanta:**

    Käytä tietokantaskeemaa (schema.sql) alustaaksesi tietokannan:

    ```sh
    psql -U your_database_username -d your_database_name -f schema.sql
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

    - Kirjautumisen jälkeen voit lisätä uuden kuitin siirtymällä osoitteeseen `/upload`.
    - Täytä kuittilomake ja tallenna kuitti tietokantaan.

3. **Tarkastele kuittien listausta:**

    - Pääsivulla (`/`) voit tarkastella kaikkia lisäämiäsi kuitteja.

4. **Hallinnoi kategorioita, tageja, maksutapoja ja myyjiä:**

    - Siirry osoitteeseen `/manage` hallinnoidaksesi näitä tietoja.

## Tulevat kehityssuunnitelmat

- Kuittien muokkaamistoiminnon lisääminen.
- Tiedostojen automaattisen nimeämisen lisääminen.
- Yksityiskohtaisten raporttien ja kulutusanalyysien kehittäminen.
- Kuittien hakutoiminnon toteuttaminen.
- Käyttöliittymän jatkokehitys ja käyttäjäkokemuksen parantaminen.
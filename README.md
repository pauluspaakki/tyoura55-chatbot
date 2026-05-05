# Tyoura55+ -chatbot

[Työhyvinvoinnin ja työkyvyn parantamiseen liittyvä keskusteleva tekoälybotti](https://www.tuni.fi/fi/tutkimus/tyoura55)

![kuva chatbotin käyttöliittymästä](image.png)

## Kuvaus
Tämä projekti on chatbot, jonka tarkoituksena on auttaa käyttäjää kehittämään itseään työuralla.

## Dev - ympäristön pystytys ja ohjelman käynnistys
1. Kloonaa repositorio 
2. Lataa [ollama3](https://ollama.com/library/llama3) ja requirements.txt importit:
   ```pip install -r requirements.txt```
3. Käynnistä sovellus komennoilla
   ```ollama pull gemma2:9b``` ja
   ```run app.py```
4. Avaa portissa http://localhost:5000 tai avaa frontendistä index.html-tiedosto


## Botin ominaisuudet 
Botti ymmärtää ja osaa tuottaa lähes täydellistä suomea.
Botti on mahdollista liittää ulkoiselle serverille esimerkiksi pilvipalveluihin (saattaa vaatia muokkausta koodiin).


## Lisenssi ja tekijät
[Paulus Paakki](https://github.com/pauluspaakki)

[Nelli Kemppainen](https://github.com/neplutin)

[Eevi Mäki-Uuro](https://github.com/eeveei)

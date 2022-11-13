import sqlite3
import numpy as np


def connect_db(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    return cur

def getUniqueAuthorNames(cur):
    cur.execute("SELECT DISTINCT name FROM author ORDER BY name")

    rows = cur.fetchall()
    rows = np.array(rows).flatten()

    return rows

def getAuthorIDForUniqueName(cur, name):
    cur.execute('''SELECT id FROM author WHERE name="%s"''' %name)

    rows = cur.fetchall()
    rows = np.array(rows)

    return(rows)

def getArticleID(cur,AuthorIds):
    articlesID = []

    for id in AuthorIds:
        cur.execute('''SELECT idArticle FROM author_article WHERE idAuthor="%s"''' %id[0])

        rows = cur.fetchall()
        articlesID.append(rows[0][0])

    return np.array(articlesID)

def getDiseaseIDForUniqueAuthor(cur,articlesIDs):
    diseasesIDs = []

    for id in articlesIDs:
        cur.execute(''' SELECT idDisease FROM disease_article WHERE idArticle="%s"''' %id)

        rows = cur.fetchall()
        rows = np.array(rows, dtype=int).flatten().tolist()
        diseasesIDs.extend(rows)

    return np.array(diseasesIDs)

cur = connect_db('dbRS.db')

fp_csv = open('pubmedDataset.csv','w')
fp_key_csv = open('authorKey.csv','w')

rows = getUniqueAuthorNames(cur)

id_count = 1

for name in rows:
    idAuthor = getAuthorIDForUniqueName(cur,name)
    idArticles = getArticleID(cur, idAuthor)
    idDiseases = getDiseaseIDForUniqueAuthor(cur,idArticles)

    idDisease, count = np.unique(idDiseases, return_counts=True)

    for i in range(len(idDisease)):

        fp_csv.write(str(id_count) + ',' + str(idDisease[i]) + ',' + str(count[i]) + '\n')

    fp_key_csv.write(str(id_count) + ','+ str(name.encode('utf-8')) + '\n') # This is a key between the new author id and the original author id. 
    id_count += 1


fp_csv.close()
fp_key_csv.close()

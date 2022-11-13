from Bio import Entrez
import sqlite3

def search(query, retmax):
    """
    (adapted from https://gist.github.com/bonzanini/5a4c39e4c02502a8451d)
    """
    Entrez.email = 'your.email@example.com'
    handle = Entrez.esearch(db='pubmed',
                            sort='relevant', #can also be 'pub+date', for example
                            retmax=retmax,
                            retmode='xml',
                            datetype='pdat',
                            mindate='1998',
                            maxdate='2019',
                            term=query)
    results = Entrez.read(handle)
    return results

def fetch_details(id_list):
    """
    (retrieved from https://gist.github.com/bonzanini/5a4c39e4c02502a8451d)
    """
    ids = ','.join(id_list)
    Entrez.email = 'your.email@example.com'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results


def pubmedToDb(diseases_list):
    conn = sqlite3.connect('dbRS.db') #Add sqlite database file name here / Database needs to be created. SQL commands to create: CreateTablesRS.sql
    c = conn.cursor()

    fp_dl = open(diseases_list, 'r')
    
    for d in fp_dl:
        disease = d.strip('\n')

        c.execute('''SELECT 1 FROM disease WHERE name="%s" LIMIT 1''' % disease)
        dis_exists = c.fetchone() is not None

        if dis_exists == False:
            c.execute('''INSERT INTO disease (name) VALUES ("''' + disease + '''");''')
            conn.commit()
            dbid_disease = c.lastrowid
        else:
            c.execute('''SELECT id FROM disease WHERE name="%s"''' % disease)
            dbid_disease = c.fetchone()[0]

        # esearch
        searched = False

        while searched == False:
            try:
                results = search(disease + '[MESH] AND human[MESH]', 100)  # Change retmax here
                searched = True
            except:
                searched = False

        id_list = results['IdList']

        if id_list != []:

            for pmid in id_list:
                namespacer = False

                # efetch
                try:
                    paper = fetch_details([pmid])

                except:
                    namespacer = True

                if namespacer == False:

                    c.execute('''SELECT 1 FROM article WHERE pmid="%s" LIMIT 1''' % pmid)
                    pmid_exists = c.fetchone() is not None

                    if pmid_exists == False:  # False indicates that it doesn't exist on the db

                        if paper['PubmedArticle'] != []:

                            # GET TITLE
                            if paper['PubmedArticle'][0]['MedlineCitation']['Article']['ArticleTitle'] != []:
                                title = paper['PubmedArticle'][0]['MedlineCitation']['Article']['ArticleTitle']
                                title = title.replace('"', "'")
                                if title == '':
                                    title = None
                            else:
                                title = None

                            # GET ABSTRACT
                            # (iteration is necessary because sometimes abstract is divided in parts)

                            try:
                                abstract = ''
                                for part in paper['PubmedArticle'][0]['MedlineCitation']['Article']['Abstract'][
                                    'AbstractText']:
                                    abstract = abstract + part
                                    abstract = abstract.replace('"', "'")

                            except:
                                abstract = None

                            # GET DATE
                            # the zero is necessary because 'ArticleDate' has two "entries",the date is in the first one

                            if paper['PubmedArticle'][0]['MedlineCitation']['Article']['ArticleDate'] != []:
                                year = paper['PubmedArticle'][0]['MedlineCitation']['Article']['ArticleDate'][0]['Year']
                            else:
                                year = None

                            # GET DOI
                            if paper['PubmedArticle'][0]['MedlineCitation']['Article']['ELocationID'] != []:
                                doi = paper['PubmedArticle'][0]['MedlineCitation']['Article']['ELocationID'][0]
                            else:
                                doi = None

                            # GET AUTHORS
                            author_list = []
                            try:
                                for author in paper['PubmedArticle'][0]['MedlineCitation']['Article']['AuthorList']:
                                    try:
                                        last_name = author['LastName']
                                    except:
                                        last_name = ''

                                    try:
                                        initial = author['Initials']
                                    except:
                                        initial = ''

                                    affil_before = author['AffiliationInfo']  # this is still a dictionary, each author can have more than one affiliation
                                    affil = ''
                                    for aff in affil_before:
                                        aff_corr = aff['Affiliation'].replace('"', "'")
                                        affil = affil + '///' + aff_corr  # /// is the separation between affiliations

                                    if affil == '':
                                        affil = None

                                    name = last_name + ' ' + initial
                                    if name == ' ':
                                        name = None

                                    c.execute('''SELECT 1 FROM author WHERE name="%s" and affiliation="%s"''' % (name, affil))
                                    author_exists = c.fetchone() is not None

                                    if author_exists == False:
                                        author_list.append((name, affil))

                            except:
                                pass


                        elif paper['PubmedBookArticle'] != []:

                            # GET TITLE
                            try:
                                if paper['PubmedBookArticle'][0]['BookDocument']['ArticleTitle'] != []:
                                    title = paper['PubmedBookArticle'][0]['BookDocument']['ArticleTitle']
                                    title = title.replace('"', "'")
                                    if title == '':
                                        title = None
                                else:
                                    title = None

                            except:
                                title = None

                            # GET ABSTRACT
                            abstract = ''
                            try:
                                for part in paper['PubmedBookArticle'][0]['BookDocument']['Abstract']['AbstractText']:
                                    abstract = abstract + part
                                    abstract = abstract.replace('"', "'")
                            except:
                                pass

                            # GET DATE
                            year = paper['PubmedBookArticle'][0]['PubmedBookData']['History'][0]['Year']

                            doi = ''

                            # GET AUTHORS
                            author_list = []
                            try:
                                for author in paper['PubmedBookArticle'][0]['BookDocument']['AuthorList']:
                                    try:
                                        last_name = author['LastName']
                                    except:
                                        last_name = ''

                                    try:
                                        initial = author['Initials']
                                    except:
                                        initial = ''

                                    affil_before = author['AffiliationInfo']  # this is still a dictionary, each author can have more than one affiliation
                                    affil = ''
                                    for aff in affil_before:
                                        aff_corr = aff['Affiliation'].replace('"', "'")
                                        affil = affil + '///' + aff_corr  # /// is the separation between affiliations

                                    name = last_name + ' ' + initial

                                    c.execute('''SELECT 1 FROM author WHERE name="%s" and affiliation="%s"''' % (name, affil))
                                    author_exists = c.fetchone() is not None
                                    
                                    if author_exists == False:
                                        author_list.append((name, affil))  

                            except:
                                pass

                        if author_list != []:
                            c.execute('''INSERT INTO article (pmid, title, abstract, year, doi) VALUES (?,?,?,?,?)''',
                                      (pmid, title, abstract, year, doi))
                            conn.commit()
                            dbid_article = c.lastrowid

                            for author in author_list:
                                name = author[0]
                                affil = author[1]

                                c.execute('''SELECT 1 FROM author WHERE name="%s" and affiliation="%s" LIMIT 1''' % (
                                name, affil))
                                author_exists = c.fetchone() is not None

                                if name != None:

                                    if author_exists == False:  # author does not already exist in the database
                                        c.execute('''INSERT INTO author (name, affiliation) VALUES (?,?)''',
                                                  (name, affil))
                                        conn.commit()
                                        dbid_author = c.lastrowid

                                    else:
                                        c.execute('''SELECT id FROM author WHERE name="%s" and affiliation="%s"''' % (
                                        name, affil))
                                        dbid_author = c.fetchone()[0]

                                    c.execute('''INSERT INTO author_article (idAuthor, idArticle) VALUES (?, ?)''',
                                              (dbid_author, dbid_article))
                                    conn.commit()


                    else:
                        c.execute('''SELECT id FROM article WHERE pmid=%s''' % (pmid))
                        dbid_article = c.fetchone()[0]

                    c.execute('''INSERT INTO disease_article (idDisease, idArticle) VALUES (?,?)''',
                              (dbid_disease, dbid_article))

    fp_dl.close()

    return ()

pubmedToDb('yourDiseasesFileHere.txt')  #Here call pubmedToDb with the .txt file of dieases, one disease per line


# DisRM - Disease Ratings Matrix

DisRM is an open-source dataset of implicit feedback for the recommendation of diseases. 
This is a dataset of users, items, and ratings where the users are authors from research articles, 
the items are diseases and the ratings are the number of articles an author wrote about a disease. 
The dataset is a .csv file in the format *author, disease, rating*. 
In this repository are the instructions to create a DisRM dataset. 
Additionally, you can download DisRM datasets from https://doi.org/10.6084/m9.figshare.21385233.

## Dependencies

- SqlLite
- Python >= 3.7.0 
- biopython
- sqlite3
- numpy 

## Run

To create DisRM, there are two main steps as shown in the bellow image: the data collection step where the data is retrieved from Pubmed and saved in a relational database; and the dataset creation step where the DisRM dataset is created from the data on the database. 

![methodology_scheme](/Images/methodology_scheme.JPG)

### 1. Data Collection

#### 1.1 Create the relational database
The first step is to create the necessary tables in SQLite.

##### From the command line
For this, you'll need to install SQLite in path. 
Then you can run the following command in the command line:

```
sqlite3 dbRS.db
```

This will open the SQLite shell in the command line in the intended database. Next, in the shell, you can run the SQL commands from the `CreateTablesRS.sql` file. 

##### From DB Browser for SQLite
For this, you'll need to install DB Browser for SQLite. Then you can create a new database called `dbRS.db`. Finally, you can run the SQL commands from the `CreateTablesRS.sql` file.

#### 1.2 Populate the relational database
In this step, we'll access PubMed to retrieve articles related to diseases using the file `pubmedToDatabase.py`.

##### List of diseases
The input in this step is a `.txt` file with a list of diseases, one disease per line. 
Here is an example of what that file looks like:

```
Bacterial Infections and Mycoses
Bacterial Infections
Bacteremia
Hemorrhagic Septicemia
Central Nervous System Bacterial Infections
Lyme Neuroborreliosis
Meningitis, Bacterial
Meningitis, Escherichia coli
Meningitis, Haemophilus
Meningitis, Listeria
Meningitis, Meningococcal
```

Edit the file and replace `yourDiseasesFileHere.txt` with your disease list, on line 262. 

If you want, you can use [this list](https://drive.google.com/file/d/193B3Qfmp8q9l2MRxv7zPXRSanqmTZRz_/view?usp=sharing), that corresponds to all the MeSH terms that are classified as diseases.

##### PubMed access
The code calls PubMed 2 times, using Entrez. For that, it needs an email address. In lines 8 and 25 replace `your.email@example.com` with your email address. 

##### PubMed search
You can customize the PubMed search. 
On line 10 you can change how the results are sorted.
On lines 14 and 15 you can change the search date range.

For more info on how to customize the search, see [Entrez's documentation of this method](http://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch).

##### Populate database
After all the configurations are done, you are ready to run `pubmedToDatabase.py`. When it's done, you will have the SQLite database populated with diseases, articles, authors, and their relations. 

### 2. Dataset Creation
Now that we have all the data retrieved from PubMed, we can create the dataset. It will be created by calculating how many articles an author wrote about a disease. 
For this, you just need to run the file `dbToMatrix.py` and the output will be the dataset in the file `pubmedDataset.csv`, in the format *author, disease, rating*.  

<ins>Note:</ins> in the database there are several authors with the same name but different affiliations. In this step, we merge the authors with the same name. In result, a file is created (`authorKey.csv`) with a key that matches the new author id (in the dataset) and the original author id (in the database).
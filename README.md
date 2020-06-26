# MedeinaPublicationTests

This is a repository of supporting code and assets for the paper (link). Below is an itemization of what each directory and python notebook contains.

# Auditing supporting documents and data

## Assets

This is a collection of the PNG files used in the publication. The methods to generate these PNG files are all present in their respective Jupyter notebooks.

## Dataset_list

Medeina was indexed with 20 individual sources of data, and as mentioned in the publication, the resulting index was composed of over 2.7m interactions that were relating over 38,000 species. Each of the 20 individual data sources are cited in the Dataset_list directory (under the text file). There is also another file- specStrings.py- which gives an overview of the Medeina-style dictionaries that were used to actually index each of these data sources.

## Dictionary_examples

This directory contains some example interaction CSV files and how they can be indexed into Medeina. The examples cover List formats (where each row of the CSV file is an interaction) as well as simple and more complex matrix formats.

## FoodWebs.zip 

This is a zip file containing the published report

# Test code

Before any of the testing experiments could be conducted, two important python files were created to set up the data needed to run experiments. These are itemized below:

- Firstly, generate_test_data.py was used to index each of the 1996 datasets available INDIVIDUALLY. The code sets up a "validation" directory, which creates a seperate instance of the WebStore object for each dataset. The references contained specStrings.py are crushed from the 20 seperate data sources into the 1996 individual dataset instances to do this (and hence if reproducing, you will need to download all available datasets, as listed in the Dataset_list, or send an email to me for a zip file with the data).
- kfold.py then sits as an intermediary step between the individual WebStore directories and testing code, by conducting important bulk-processing steps:
    - Firstly, 1996 possible combinations of aggregated indexes are created- that is, for every individual dataset available, combine the indexes from the other 1995 datasets. The result is a list of indexes that each have one of the 1996 datasets missing.
    - For each of the 1996 datasets, we locate the index that missed it out. The names of this test dataset are crushed into a simple list, and an instance of the Web object is set up, which points to this located index. Pass this list into the Web.apply() method, and collect the results (along with other meta data such as time of exection, original names in the list etc).
    - Repeat this for the exact matching, genus, and family levels.

The result of kfold.py are 1996 folders that contain python-serialized objects storing results. These can simply be picked up in the Jupyter notebooks that actually aggregate and analyse the data.

to reproduce the results, you will need to:

- Collect the datasets, either following through the citation links, or emailing me 
- Run the generate_test_data.py function to create the validation directory, containing the indexes with one dataset only
- Run the applyIndividual() function in kfold.py, passing a name from the validation directory, which constructs an index containing all datasets other than the provided name, and saves the results to a results directory (that you will need to enter).

## Accuracy.ipynb

This contains two main results:

- The larger heatmaps that focus on precision and recall of each of the taxonomic generalisations
- The smaller, example confusion matrices that provide insight into some of the categories of results for exact matching

## Example.ipynb

This simply generates the example network from section 6 of the publication

## Popularity.ipynb

This is the code that provides a quick analysis of the most popular species, and most popular interactions, occuring in the full Medeina index

## Scale.ipynb

This is the code that applies Medeina's full dataset index to the Isle of Eigg dataset. The dataset for the Isle of Eigg, or any other chosen location, can be downloaded from [NBN Atlas](https://nbnatlas.org/). The notebook then runs the species from the NBN dataset through Medeina. 

The networks themselves aren't drawn through networkx as the Example network is; rather, the audit function is called to obtain information about all interactions, and this is then passed to the Cytoscape software for drawing.

## Usablity.ipynb

This notebook draws some basic charts that analyse usability metrics of Medeina, including timing translation and network building functions, as well as calculations of species involvements and translation successes

# Known Issues with Medeina at present

There are some known issues with the data currently held in the index. Namely:

- If you will be using the pre-packaged data store, be advised that some of the indexed datasets sometimes reversed the convention of how predator-prey interactions are actually held, causing the underlying interactions to be inferred as (prey,predator). Hence, while only a small amount of data was affected by this, it may be advisable to use undirected graphs from the pre-packaged web store only.
- There are some data points that give counterproductive output from the EcoNameTranslator. We are working on a method to filter such data points autonomously.
